import re
from typing import Dict, Any, Optional
from fastapi import HTTPException, status


class NaturalLanguageParser:
    def __init__(self):
        self.patterns = {
            "palindrome": [
                r"\bpalindrom",  # palindrome, palindromic
                r"reads the same",
                r"same forwards and backwards",
            ],
            "word_count": [
                r"\bsingle word\b",
                r"\bone word\b",
                r"\btwo words\b",
                r"\bthree words\b",
                r"\bfour words\b",
                r"\bfive words\b",
                r"\b(\d+) words?\b",
            ],
            "length": [
                r"longer than (\d+) characters?",
                r"shorter than (\d+) characters?",
                r"length (?:greater than|more than) (\d+)",
                r"length (?:less than|under) (\d+)",
                r"(\d+) characters? (?:or )?longer",
                r"(\d+) characters? (?:or )?shorter",
                r"between (\d+) and (\d+) characters?",
            ],
            "contains_character": [
                r"contain(?:s|ing)? the letter ([a-zA-Z])",
                r"contain(?:s|ing)? ([a-zA-Z])",
                r"has the letter ([a-zA-Z])",
                r"with ([a-zA-Z])",
                r"that have ([a-zA-Z])",
            ],
            "vowels": [r"vowel", r"[aeiou]"],
        }

        self.vowels = {"a", "e", "i", "o", "u"}

    def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Parse natural language query and convert to filters
        """
        query_lower = query.lower().strip()
        filters = {}

        try:
            # Check for palindrome
            if any(
                re.search(pattern, query_lower)
                for pattern in self.patterns["palindrome"]
            ):
                filters["is_palindrome"] = True

            # Parse word count
            word_count = self._parse_word_count(query_lower)
            if word_count is not None:
                filters["word_count"] = word_count

            # Parse length filters
            length_filters = self._parse_length_filters(query_lower)
            filters.update(length_filters)

            # Parse character containment
            char_filter = self._parse_character_filter(query_lower)
            if char_filter:
                filters["contains_character"] = char_filter

            # Handle vowel references
            if any(
                re.search(pattern, query_lower) for pattern in self.patterns["vowels"]
            ):
                # Default to 'a' as the first vowel if no specific character is mentioned
                if "contains_character" not in filters:
                    filters["contains_character"] = "a"

            # Validate no conflicting filters
            self._validate_filters(filters)

            return filters

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to parse natural language query: {str(e)}",
            )

    def _parse_word_count(self, query: str) -> Optional[int]:
        """Parse word count from natural language"""
        # Exact numbers
        match = re.search(r"\b(\d+) words?\b", query)
        if match:
            return int(match.group(1))

        # Common phrases
        if re.search(r"\bsingle word\b|\bone word\b", query):
            return 1
        elif re.search(r"\btwo words\b", query):
            return 2
        elif re.search(r"\bthree words\b", query):
            return 3
        elif re.search(r"\bfour words\b", query):
            return 4
        elif re.search(r"\bfive words\b", query):
            return 5

        return None

    def _parse_length_filters(self, query: str) -> Dict[str, Any]:
        """Parse length-related filters"""
        filters = {}

        # Longer than X characters
        match = re.search(r"longer than (\d+) characters?", query)
        if match:
            filters["min_length"] = int(match.group(1)) + 1

        # Shorter than X characters
        match = re.search(r"shorter than (\d+) characters?", query)
        if match:
            filters["max_length"] = int(match.group(1)) - 1

        # Greater than/more than
        match = re.search(r"length (?:greater than|more than) (\d+)", query)
        if match:
            filters["min_length"] = int(match.group(1)) + 1

        # Less than/under
        match = re.search(r"length (?:less than|under) (\d+)", query)
        if match:
            filters["max_length"] = int(match.group(1)) - 1

        # X characters or longer
        match = re.search(r"(\d+) characters? (?:or )?longer", query)
        if match:
            filters["min_length"] = int(match.group(1))

        # X characters or shorter
        match = re.search(r"(\d+) characters? (?:or )?shorter", query)
        if match:
            filters["max_length"] = int(match.group(1))

        # Between X and Y characters
        match = re.search(r"between (\d+) and (\d+) characters?", query)
        if match:
            filters["min_length"] = int(match.group(1))
            filters["max_length"] = int(match.group(2))

        return filters

    def _parse_character_filter(self, query: str) -> Optional[str]:
        """Parse character containment filters"""
        # Specific letter mentioned
        match = re.search(r"contain(?:s|ing)? the letter ([a-zA-Z])", query)
        if match:
            return match.group(1).lower()

        match = re.search(r"contain(?:s|ing)? ([a-zA-Z])", query)
        if match:
            return match.group(1).lower()

        match = re.search(r"has the letter ([a-zA-Z])", query)
        if match:
            return match.group(1).lower()

        match = re.search(r"with ([a-zA-Z])", query)
        if match:
            return match.group(1).lower()

        match = re.search(r"that have ([a-zA-Z])", query)
        if match:
            return match.group(1).lower()

        return None

    def _validate_filters(self, filters: Dict[str, Any]):
        """Validate that filters don't conflict"""
        if "min_length" in filters and "max_length" in filters:
            if filters["min_length"] > filters["max_length"]:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Conflicting filters: min_length cannot be greater than max_length",
                )

        # Check for empty filters (query understood but no valid filters extracted)
        if not filters:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to extract meaningful filters from the query",
            )
