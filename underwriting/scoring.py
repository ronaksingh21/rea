from __future__ import annotations

from datetime import datetime
from agent.models import ExtractedDeal, UnderwritingResult
from underwriting.config import DEFAULT_THRESHOLDS, DEFAULT_WEIGHTS


def _months_until(date_str: str) -> float | None:
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            dt = datetime.strptime(date_str, fmt)
            now = datetime.now()
            return (dt.year - now.year) * 12 + (dt.month - now.month)
        except Exception:
            continue
    return None


def run_underwriting(deal: ExtractedDeal) -> UnderwritingResult:
    warnings: list[str] = []

    calculated_cap_rate = None
    if deal.noi and deal.purchase_price and deal.purchase_price > 0:
        calculated_cap_rate = deal.noi / deal.purchase_price

    lease_months = []
    for rr in deal.rent_roll:
        if rr.lease_end:
            m = _months_until(rr.lease_end)
            if m is not None:
                lease_months.append(m)

    avg_lease_term = sum(lease_months) / len(lease_months) if lease_months else None

    expiring_24 = None
    if lease_months:
        expiring_24 = 100.0 * len([m for m in lease_months if m <= 24]) / len(lease_months)

    concentration = None
    tenant_pcts = [r.percent_of_income for r in deal.rent_roll if r.percent_of_income is not None]
    if tenant_pcts:
        concentration = max(tenant_pcts)

    rent_psf = []
    for rr in deal.rent_roll:
        if rr.annual_rent and rr.sqft and rr.sqft > 0:
            rent_psf.append(rr.annual_rent / rr.sqft)
    avg_rent_psf = sum(rent_psf) / len(rent_psf) if rent_psf else None

    score = 0
    t = DEFAULT_THRESHOLDS
    w = DEFAULT_WEIGHTS

    if expiring_24 is not None:
        if expiring_24 > t.expiry_high_pct:
            score += w.lease_expiry_high
        elif expiring_24 > t.expiry_med_pct:
            score += w.lease_expiry_med

    if concentration is not None:
        if concentration > t.concentration_high_pct:
            score += w.concentration_high
        elif concentration > t.concentration_med_pct:
            score += w.concentration_med

    if calculated_cap_rate is not None and deal.reported_cap_rate is not None:
        reported = deal.reported_cap_rate
        if reported > 1.0:
            reported = reported / 100.0
        diff_pct = abs(calculated_cap_rate - reported) / (reported or 1)
        if diff_pct > t.caprate_diff_max:
            score += w.caprate_mismatch
            warnings.append("Calculated cap rate differs from reported by >3%")

    if deal.purchase_price is None or deal.noi is None:
        score += w.missing_core_fields
        warnings.append("Missing purchase_price or NOI")

    if not deal.rent_roll:
        score += w.missing_rent_roll
        warnings.append("Rent roll not extracted")

    if not deal.lease_expiration_dates:
        score += w.missing_lease_expiries
        warnings.append("Lease expiration dates missing")

    if score >= 60:
        label = "High"
    elif score >= 30:
        label = "Medium"
    else:
        label = "Low"

    return UnderwritingResult(
        calculated_cap_rate=calculated_cap_rate,
        avg_lease_term_months=avg_lease_term,
        lease_expiry_24m_percent=expiring_24,
        tenant_concentration_percent=concentration,
        avg_rent_per_sqft=avg_rent_psf,
        risk_score=score,
        risk_label=label,
        warnings=warnings,
    )
