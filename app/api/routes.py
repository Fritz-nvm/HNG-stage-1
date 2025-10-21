from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from infrastructure.models import StringAnalysis, StringAnalysisCreate
from application.services import StringAnalysisService
from infrastructure.database import get_db

router = APIRouter()
string_service = StringAnalysisService()

@router.post(
    "/strings",
    response_model=StringAnalysis,
    status_code=status.HTTP_201_CREATED
)
async def create_analyze_string(
    string_data: StringAnalysisCreate, 
    db: Session = Depends(get_db)
):
    if string_service.string_exists(db, string_data.value):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="String already exists in the system"
        )
    
    analysis = string_service.analyze_string(string_data.value)
    
    if not string_service.store_analysis(db, analysis):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store analysis"
        )
    
    return analysis

@router.get("/strings/{analysis_id}", response_model=StringAnalysis)
async def get_string_analysis(analysis_id: str, db: Session = Depends(get_db)):
    analysis = string_service.get_analysis(db, analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="String analysis not found"
        )
    
    return analysis

@router.get("/strings", response_model=list[StringAnalysis])
async def get_all_string_analyses(db: Session = Depends(get_db)):
    return string_service.get_all_analyses(db)