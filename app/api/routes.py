from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.infrastructure.models import (
    StringAnalysis,
    StringAnalysisCreate,
    FilteredStringsResponse,
    NaturalLanguageResponse,
    NaturalLanguageInterpretation,
)
from app.application.services import StringAnalysisService
from app.application.natural_language_parser import NaturalLanguageParser

from app.infrastructure.database import get_db
from typing import Optional
from fastapi import Query


router = APIRouter()
string_service = StringAnalysisService()


@router.post(
    "/strings", response_model=StringAnalysis, status_code=status.HTTP_201_CREATED
)
async def create_string(
    string_data: StringAnalysisCreate, db: Session = Depends(get_db)
):
    if string_service.string_exists(db, string_data.value):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="String already exists in the system",
        )

    analysis = string_service.analyze_string(string_data.value)

    if not string_service.store_analysis(db, analysis):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store analysis",
        )

    return analysis


@router.get(
    "/strings/{string_value}",
    response_model=StringAnalysis,
    summary="Get string analysis by string value",
    description="Retrieve stored string analysis by the original string value",
    responses={
        200: {"description": "String analysis found successfully"},
        404: {"description": "String does not exist in the system"},
    },
)
async def get_string_analysis_by_value(
    string_value: str, db: Session = Depends(get_db)
):
    """
    Get string analysis by the original string value.

    - **string_value**: The original string to look up

    Returns the string analysis if found, or 404 if not exists.
    """
    analysis = string_service.get_analysis_by_string_value(db, string_value)

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="String does not exist in the system",
        )

    return analysis


@router.get(
    "/strings",
    response_model=FilteredStringsResponse,
    summary="Get all strings with filtering",
    description="Retrieve stored string analyses with optional filters",
    responses={
        200: {"description": "Strings retrieved successfully"},
        400: {"description": "Invalid query parameter values or types"},
    },
)
async def get_all_string_analyses(
    db: Session = Depends(get_db),
    is_palindrome: Optional[bool] = Query(
        None, description="Filter by palindrome status"
    ),
    min_length: Optional[int] = Query(None, ge=0, description="Minimum string length"),
    max_length: Optional[int] = Query(None, ge=1, description="Maximum string length"),
    word_count: Optional[int] = Query(None, ge=0, description="Exact word count"),
    contains_character: Optional[str] = Query(
        None, min_length=1, max_length=1, description="Single character to search for"
    ),
):
    """
    Get all string analyses with optional filtering.

    Query Parameters:
    - **is_palindrome**: boolean (true/false) - Filter by palindrome status
    - **min_length**: integer - Minimum string length
    - **max_length**: integer - Maximum string length
    - **word_count**: integer - Exact word count
    - **contains_character**: string - Single character to search for

    Returns filtered results with count and applied filters.
    """
    # Validate parameter combinations
    if min_length is not None and max_length is not None and min_length > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_length cannot be greater than max_length",
        )

    if contains_character and len(contains_character) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="contains_character must be exactly one character",
        )

    # Get filtered analyses
    analyses = string_service.get_filtered_analyses(
        db=db,
        is_palindrome=is_palindrome,
        min_length=min_length,
        max_length=max_length,
        word_count=word_count,
        contains_character=contains_character,
    )

    # Build filters applied object
    filters_applied = {}
    if is_palindrome is not None:
        filters_applied["is_palindrome"] = is_palindrome
    if min_length is not None:
        filters_applied["min_length"] = min_length
    if max_length is not None:
        filters_applied["max_length"] = max_length
    if word_count is not None:
        filters_applied["word_count"] = word_count
    if contains_character is not None:
        filters_applied["contains_character"] = contains_character

    return FilteredStringsResponse(
        data=analyses, count=len(analyses), filters_applied=filters_applied
    )


from application.natural_language_parser import NaturalLanguageParser


@router.get(
    "/strings/filter-by-natural-language",
    response_model=NaturalLanguageResponse,
    summary="Filter strings by natural language query",
    description="Retrieve string analyses using natural language queries",
    responses={
        200: {"description": "Strings retrieved successfully"},
        400: {"description": "Unable to parse natural language query"},
        422: {"description": "Query parsed but resulted in conflicting filters"},
    },
)
async def filter_by_natural_language(query: str, db: Session = Depends(get_db)):
    """
    Filter strings using natural language queries.

    - **query**: Natural language query string

    Supported query patterns:
    - "all single word palindromic strings" → word_count=1, is_palindrome=true
    - "strings longer than 10 characters" → min_length=11
    - "palindromic strings that contain the first vowel" → is_palindrome=true, contains_character=a
    - "strings containing the letter z" → contains_character=z
    - "two word strings" → word_count=2
    - "strings between 5 and 15 characters" → min_length=5, max_length=15
    """
    try:
        analyses, parsed_filters = string_service.get_analyses_by_natural_language(
            db, query
        )

        interpretation = NaturalLanguageInterpretation(
            original=query, parsed_filters=parsed_filters
        )

        return NaturalLanguageResponse(
            data=analyses, count=len(analyses), interpreted_query=interpretation
        )

    except HTTPException:
        # Re-raise HTTP exceptions from the parser
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unable to process natural language query: {str(e)}",
        )


@router.delete(
    "/strings/{string_value}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete string analysis by string value",
    description="Delete a stored string analysis by the original string value",
    responses={
        204: {"description": "String analysis deleted successfully"},
        404: {"description": "String does not exist in the system"},
    },
)
async def delete_string_analysis(string_value: str, db: Session = Depends(get_db)):
    """
    Delete string analysis by the original string value.

    - **string_value**: Original string value to delete

    Returns 204 No Content on success.
    """
    # Check if exists first
    if not string_service.string_exists(db, string_value):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="String does not exist in the system",
        )

    # Delete the analysis
    if not string_service.delete_analysis_by_string_value(db, string_value):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete string analysis",
        )

    # Return 204 No Content with empty body
    return None
