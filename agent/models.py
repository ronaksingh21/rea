from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class RentRollRow(BaseModel):
    unit: Optional[str] = None
    tenant_name: Optional[str] = None
    sqft: Optional[float] = None
    annual_rent: Optional[float] = None
    monthly_rent: Optional[float] = None
    lease_start: Optional[str] = None
    lease_end: Optional[str] = None
    percent_of_income: Optional[float] = None


class ExtractedDeal(BaseModel):
    property_name: Optional[str] = None
    address: Optional[str] = None
    purchase_price: Optional[float] = None
    noi: Optional[float] = None
    reported_cap_rate: Optional[float] = None
    rent_roll: List[RentRollRow] = Field(default_factory=list)
    lease_expiration_dates: List[str] = Field(default_factory=list)


class UnderwritingResult(BaseModel):
    calculated_cap_rate: Optional[float] = None
    avg_lease_term_months: Optional[float] = None
    lease_expiry_24m_percent: Optional[float] = None
    tenant_concentration_percent: Optional[float] = None
    avg_rent_per_sqft: Optional[float] = None
    risk_score: int
    risk_label: str
    warnings: List[str] = Field(default_factory=list)


class DealRecord(BaseModel):
    message_id: str
    subject: str
    sender: str
    received_at: datetime
    pdf_path: str
    extracted: ExtractedDeal
    underwriting: UnderwritingResult
