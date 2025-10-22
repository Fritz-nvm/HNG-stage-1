from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


# SQLAlchemy Model for database
class StringAnalysisDB(Base):
    __tablename__ = "string_analyses"

    id = Column(String(64), primary_key=True)  # SHA256 hash
    value = Column(String, nullable=False)
    length = Column(Integer, nullable=False)
    is_palindrome = Column(Boolean, nullable=False)
    unique_characters = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    sha256_hash = Column(String(64), nullable=False)
    character_frequency_map = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False)


# Pydantic models for API
class StringProperties(BaseModel):
    length: int
    is_palindrome: bool
    unique_characters: int
    word_count: int
    sha256_hash: str
    character_frequency_map: Dict[str, int]


class StringAnalysis(BaseModel):
    id: str
    value: str
    properties: StringProperties
    created_at: datetime


class StringAnalysisCreate(BaseModel):
    value: str = Field(..., min_length=1, description="String to analyze")


class FilteredStringsResponse(BaseModel):
    data: List[StringAnalysis]
    count: int
    filters_applied: Dict[str, Optional[str | int | bool]]


class StringFilters(BaseModel):
    is_palindrome: Optional[bool] = None
    min_length: Optional[int] = Field(None, ge=0, description="Minimum string length")
    max_length: Optional[int] = Field(None, ge=1, description="Maximum string length")
    word_count: Optional[int] = Field(None, ge=0, description="Exact word count")
    contains_character: Optional[str] = Field(
        None, min_length=1, max_length=1, description="Single character to search for"
    )


class NaturalLanguageInterpretation(BaseModel):
    original: str
    parsed_filters: Dict[str, Any]


class NaturalLanguageResponse(BaseModel):
    data: List[StringAnalysis]
    count: int
    interpreted_query: NaturalLanguageInterpretation
