from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Company
from app.schemas import CompanyResponse

router = APIRouter()

# Mock companies data - will be loaded on startup
MOCK_COMPANIES = [
    {"code": "005930", "name": "삼성전자", "market": "KOSPI", "sector": "전자"},
    {"code": "373220", "name": "LG에너지솔루션", "market": "KOSPI", "sector": "배터리"},
    {"code": "000660", "name": "SK하이닉스", "market": "KOSPI", "sector": "반도체"},
    {"code": "005380", "name": "현대차", "market": "KOSPI", "sector": "자동차"},
    {"code": "035420", "name": "NAVER", "market": "KOSPI", "sector": "IT"},
    {"code": "051910", "name": "LG화학", "market": "KOSPI", "sector": "화학"},
    {"code": "006400", "name": "삼성SDI", "market": "KOSPI", "sector": "배터리"},
    {"code": "068270", "name": "셀트리온", "market": "KOSPI", "sector": "바이오"},
    {"code": "207940", "name": "삼성바이오로직스", "market": "KOSPI", "sector": "바이오"},
    {"code": "028260", "name": "삼성물산", "market": "KOSPI", "sector": "지주사"},
]

@router.get("/search", response_model=List[CompanyResponse])
def search_companies(
    q: str = Query(..., min_length=1, description="Search query"),
    db: Session = Depends(get_db)
):
    """Search companies by name or code"""
    # Try database first, fallback to mock data
    companies = db.query(Company).filter(
        (Company.name.contains(q)) | (Company.code.contains(q))
    ).all()

    if companies:
        return companies

    # Filter mock companies
    filtered = [c for c in MOCK_COMPANIES if q in c["name"] or q in c["code"]]
    return [CompanyResponse(id=i+1, **c) for i, c in enumerate(filtered)]

@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(company_id: int, db: Session = Depends(get_db)):
    """Get company by ID"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if company:
        return company

    # Fallback to mock data
    if 1 <= company_id <= len(MOCK_COMPANIES):
        mock_company = MOCK_COMPANIES[company_id - 1]
        return CompanyResponse(id=company_id, **mock_company)

    raise HTTPException(status_code=404, detail="Company not found")
