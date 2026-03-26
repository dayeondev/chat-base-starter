from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    market = Column(String(20))  # KOSPI, KOSDAQ, KONEX
    sector = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    disclosures = relationship("Disclosure", back_populates="company")

class Disclosure(Base):
    __tablename__ = "disclosures"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(String(1000))
    report_date = Column(DateTime, nullable=False)
    filed_date = Column(DateTime, default=datetime.utcnow)
    url = Column(String(500))

    company = relationship("Company", back_populates="disclosures")
