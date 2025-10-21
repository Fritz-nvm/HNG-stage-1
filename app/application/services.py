import hashlib
from typing import Dict
from datetime import datetime
from sqlalchemy.orm import Session
from infrastructure.models import StringAnalysis, StringProperties, StringAnalysisDB

class StringAnalysisService:
    
    def _compute_sha256_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def _compute_character_frequency(self, text: str) -> Dict[str, int]:
        frequency_map = {}
        for char in text:
            frequency_map[char] = frequency_map.get(char, 0) + 1
        return frequency_map

    def _is_palindrome(self, text: str) -> bool:
        cleaned_text = ''.join(char.lower() for char in text if char.isalnum())
        return cleaned_text == cleaned_text[::-1]

    def _count_unique_characters(self, text: str) -> int:
        return len(set(text))

    def _count_words(self, text: str) -> int:
        return len(text.split())

    def analyze_string(self, text: str) -> StringAnalysis:
        sha256_hash = self._compute_sha256_hash(text)
        char_frequency = self._compute_character_frequency(text)
        
        properties = StringProperties(
            length=len(text),
            is_palindrome=self._is_palindrome(text),
            unique_characters=self._count_unique_characters(text),
            word_count=self._count_words(text),
            sha256_hash=sha256_hash,
            character_frequency_map=char_frequency
        )
        
        analysis = StringAnalysis(
            id=sha256_hash,
            value=text,
            properties=properties,
            created_at=datetime.utcnow()
        )
        
        return analysis

    def store_analysis(self, db: Session, analysis: StringAnalysis) -> bool:
        # Check if already exists
        existing = db.query(StringAnalysisDB).filter(StringAnalysisDB.id == analysis.id).first()
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
            created_at=analysis.created_at
        )
        
        db.add(db_analysis)
        db.commit()
        return True

    def get_analysis(self, db: Session, analysis_id: str) -> StringAnalysis | None:
        db_analysis = db.query(StringAnalysisDB).filter(StringAnalysisDB.id == analysis_id).first()
        if not db_analysis:
            return None
        
        properties = StringProperties(
            length=db_analysis.length,
            is_palindrome=db_analysis.is_palindrome,
            unique_characters=db_analysis.unique_characters,
            word_count=db_analysis.word_count,
            sha256_hash=db_analysis.sha256_hash,
            character_frequency_map=db_analysis.character_frequency_map
        )
        
        return StringAnalysis(
            id=db_analysis.id,
            value=db_analysis.value,
            properties=properties,
            created_at=db_analysis.created_at
        )

    def string_exists(self, db: Session, text: str) -> bool:
        sha256_hash = self._compute_sha256_hash(text)
        return db.query(StringAnalysisDB).filter(StringAnalysisDB.id == sha256_hash).first() is not None

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
                character_frequency_map=db_analysis.character_frequency_map
            )
            
            analysis = StringAnalysis(
                id=db_analysis.id,
                value=db_analysis.value,
                properties=properties,
                created_at=db_analysis.created_at
            )
            analyses.append(analysis)
        
        return analyses