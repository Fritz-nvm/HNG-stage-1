import hashlib
from typing import Dict, Optional, List, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.infrastructure.models import StringAnalysis, StringProperties, StringAnalysisDB
from fastapi import HTTPException, status


class StringAnalysisService:

    def _compute_sha256_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _compute_character_frequency(self, text: str) -> Dict[str, int]:
        frequency_map = {}
        for char in text:
            frequency_map[char] = frequency_map.get(char, 0) + 1
        return frequency_map

    def _is_palindrome(self, text: str) -> bool:
        cleaned_text = "".join(char.lower() for char in text if char.isalnum())
        return cleaned_text == cleaned_text[::-1]

    def _count_unique_characters(self, text: str) -> int:
        return len(set(text))

    def _count_words(self, text: str) -> int:
        return len(text.split())

    def get_analysis_by_string_value(
        self, db: Session, string_value: str
    ) -> StringAnalysis | None:
        # Compute the SHA256 hash to find the record
        sha256_hash = self._compute_sha256_hash(string_value)

        db_analysis = (
            db.query(StringAnalysisDB)
            .filter(StringAnalysisDB.id == sha256_hash)
            .first()
        )
        if not db_analysis:
            return None

        properties = StringProperties(
            length=db_analysis.length,
            is_palindrome=db_analysis.is_palindrome,
            unique_characters=db_analysis.unique_characters,
            word_count=db_analysis.word_count,
            sha256_hash=db_analysis.sha256_hash,
            character_frequency_map=db_analysis.character_frequency_map,
        )

        return StringAnalysis(
            id=db_analysis.id,
            value=db_analysis.value,
            properties=properties,
            created_at=db_analysis.created_at,
        )

    def get_analyses_by_natural_language(self, db: Session, query: str):
        """
        Get analyses using natural language query
        Returns tuple of (analyses, parsed_filters)
        """
        print(f"🎯 Service layer processing NLP query: '{query}'")

        try:
            # Parse natural language query
            parsed_filters = self.nlp_parser.parse_query(query)
            print(f"✅ Service received parsed filters: {parsed_filters}")

            # Use existing filtered analysis method
            analyses = self.get_filtered_analyses(db, **parsed_filters)
            print(f"✅ Service found {len(analyses)} matching analyses")

            return analyses, parsed_filters

        except HTTPException as he:
            print(f"❌ Service caught HTTPException: {he.detail}")
            raise he
        except Exception as e:
            print(f"❌ Service caught unexpected error: {str(e)}")
            import traceback

            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to process natural language query: {str(e)}",
            )

    def get_filtered_analyses(
        self,
        db: Session,
        is_palindrome: Optional[bool] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        word_count: Optional[int] = None,
        contains_character: Optional[str] = None,
    ) -> List[StringAnalysis]:
        """Get analyses with optional filters (compatible approach)"""
        # Get all analyses first
        all_analyses = self.get_all_analyses(db)

        # Apply filters in Python
        filtered_analyses = all_analyses

        if is_palindrome is not None:
            filtered_analyses = [
                a
                for a in filtered_analyses
                if a.properties.is_palindrome == is_palindrome
            ]

        if min_length is not None:
            filtered_analyses = [
                a for a in filtered_analyses if a.properties.length >= min_length
            ]

        if max_length is not None:
            filtered_analyses = [
                a for a in filtered_analyses if a.properties.length <= max_length
            ]

        if word_count is not None:
            filtered_analyses = [
                a for a in filtered_analyses if a.properties.word_count == word_count
            ]

        if contains_character is not None:
            filtered_analyses = [
                a
                for a in filtered_analyses
                if contains_character in a.properties.character_frequency_map
            ]

        return filtered_analyses

    def analyze_string(self, text: str) -> StringAnalysis:
        sha256_hash = self._compute_sha256_hash(text)
        char_frequency = self._compute_character_frequency(text)

        properties = StringProperties(
            length=len(text),
            is_palindrome=self._is_palindrome(text),
            unique_characters=self._count_unique_characters(text),
            word_count=self._count_words(text),
            sha256_hash=sha256_hash,
            character_frequency_map=char_frequency,
        )

        analysis = StringAnalysis(
            id=sha256_hash,
            value=text,
            properties=properties,
            created_at=datetime.utcnow(),
        )

        return analysis

    def store_analysis(self, db: Session, analysis: StringAnalysis) -> bool:
        # Check if already exists
        existing = (
            db.query(StringAnalysisDB)
            .filter(StringAnalysisDB.id == analysis.id)
            .first()
        )
        if existing:
            return False

        # Create database record
        db_analysis = StringAnalysisDB(
            id=analysis.id,
            value=analysis.value,
            length=analysis.properties.length,
            is_palindrome=analysis.properties.is_palindrome,
            unique_characters=analysis.properties.unique_characters,
            word_count=analysis.properties.word_count,
            sha256_hash=analysis.properties.sha256_hash,
            character_frequency_map=analysis.properties.character_frequency_map,
            created_at=analysis.created_at,
        )

        db.add(db_analysis)
        db.commit()
        return True

    def get_analysis(self, db: Session, analysis_id: str) -> StringAnalysis | None:
        db_analysis = (
            db.query(StringAnalysisDB)
            .filter(StringAnalysisDB.id == analysis_id)
            .first()
        )
        if not db_analysis:
            return None

        properties = StringProperties(
            length=db_analysis.length,
            is_palindrome=db_analysis.is_palindrome,
            unique_characters=db_analysis.unique_characters,
            word_count=db_analysis.word_count,
            sha256_hash=db_analysis.sha256_hash,
            character_frequency_map=db_analysis.character_frequency_map,
        )

        return StringAnalysis(
            id=db_analysis.id,
            value=db_analysis.value,
            properties=properties,
            created_at=db_analysis.created_at,
        )

    def string_exists(self, db: Session, text: str) -> bool:
        sha256_hash = self._compute_sha256_hash(text)
        return (
            db.query(StringAnalysisDB)
            .filter(StringAnalysisDB.id == sha256_hash)
            .first()
            is not None
        )

    def get_all_analyses(self, db: Session) -> list[StringAnalysis]:
        db_analyses = db.query(StringAnalysisDB).all()
        analyses = []

        for db_analysis in db_analyses:
            properties = StringProperties(
                length=db_analysis.length,
                is_palindrome=db_analysis.is_palindrome,
                unique_characters=db_analysis.unique_characters,
                word_count=db_analysis.word_count,
                sha256_hash=db_analysis.sha256_hash,
                character_frequency_map=db_analysis.character_frequency_map,
            )

            analysis = StringAnalysis(
                id=db_analysis.id,
                value=db_analysis.value,
                properties=properties,
                created_at=db_analysis.created_at,
            )
            analyses.append(analysis)

        return analyses

    def delete_analysis(self, db: Session, analysis_id: str) -> bool:
        """Delete analysis by ID (SHA256 hash)"""
        db_analysis = (
            db.query(StringAnalysisDB)
            .filter(StringAnalysisDB.id == analysis_id)
            .first()
        )

        if not db_analysis:
            return False

        db.delete(db_analysis)
        db.commit()
        return True

    def delete_analysis_by_string_value(self, db: Session, string_value: str) -> bool:
        """Delete analysis by string value"""
        sha256_hash = self._compute_sha256_hash(string_value)
        return self.delete_analysis(db, sha256_hash)

    def get_string_value_by_id(self, db: Session, analysis_id: str) -> Optional[str]:
        """Get the original string value by ID"""
        db_analysis = (
            db.query(StringAnalysisDB)
            .filter(StringAnalysisDB.id == analysis_id)
            .first()
        )
        return db_analysis.value if db_analysis else None
