from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CompanyBase(BaseModel):
    code: str
    name: str
    market: Optional[str] = None
    sector: Optional[str] = None

class CompanyResponse(CompanyBase):
    id: int

    class Config:
        from_attributes = True

class DisclosureBase(BaseModel):
    company_id: int
    title: str
    content: Optional[str] = None
    report_date: datetime
    url: Optional[str] = None

class DisclosureResponse(DisclosureBase):
    id: int
    filed_date: datetime

    class Config:
        from_attributes = True
