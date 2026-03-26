from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Disclosure
from app.schemas import DisclosureResponse

router = APIRouter()

# Mock disclosures data
MOCK_DISCLOSURES = [
    {
        "company_id": 1,
        "title": "분기보고서",
        "content": "2024년 4분기 분기보고서",
        "report_date": "2025-02-20",
        "url": "https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20250220000123"
    },
    {
        "company_id": 1,
        "title": "주주총회 소집 통지",
        "content": "제85기 정기주주총회 소집 통지",
        "report_date": "2025-02-15",
        "url": "https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20250215000456"
    },
    {
        "company_id": 2,
        "title": "반기보고서",
        "content": "2024년 반기보고서",
        "report_date": "2025-02-18",
        "url": "https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20250218000789"
    },
    {
        "company_id": 3,
        "title": "사업보고서",
        "content": "2024년 사업보고서",
        "report_date": "2025-02-22",
        "url": "https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20250222000111"
    },
]

@router.get("/company/{company_id}", response_model=List[DisclosureResponse])
def get_disclosures_by_company(
    company_id: int,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get disclosures for a specific company"""
    disclosures = db.query(Disclosure).filter(
        Disclosure.company_id == company_id
    ).order_by(Disclosure.report_date.desc()).limit(limit).all()

    if disclosures:
        return disclosures

    # Filter mock disclosures
    filtered = [d for d in MOCK_DISCLOSURES if d["company_id"] == company_id]
    return [
        DisclosureResponse(
            id=i+1,
            filed_date=datetime.now(),
            company_id=d["company_id"],
            title=d["title"],
            content=d["content"],
            report_date=datetime.fromisoformat(d["report_date"]),
            url=d.get("url")
        )
        for i, d in enumerate(filtered[:limit])
    ]

@router.get("/latest", response_model=List[DisclosureResponse])
def get_latest_disclosures(
    company_ids: str = Query(None, description="Comma-separated company IDs"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get latest disclosures, optionally filtered by company IDs"""
    query = db.query(Disclosure).order_by(Disclosure.report_date.desc())

    if company_ids:
        ids = [int(id.strip()) for id in company_ids.split(",")]
        query = query.filter(Disclosure.company_id.in_(ids))

    disclosures = query.limit(limit).all()

    if disclosures:
        return disclosures

    # Return mock disclosures
    result = []
    for i, d in enumerate(MOCK_DISCLOSURES):
        if company_ids and d["company_id"] not in [int(id.strip()) for id in company_ids.split(",")]:
            continue
        result.append(
            DisclosureResponse(
                id=i+1,
                filed_date=datetime.now(),
                company_id=d["company_id"],
                title=d["title"],
                content=d["content"],
                report_date=datetime.fromisoformat(d["report_date"]),
                url=d.get("url")
            )
        )
    return result[:limit]
