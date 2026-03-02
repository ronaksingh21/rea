from dataclasses import dataclass


@dataclass
class RiskWeights:
    lease_expiry_high: int = 35
    lease_expiry_med: int = 20
    concentration_high: int = 35
    concentration_med: int = 20
    caprate_mismatch: int = 20
    missing_core_fields: int = 10


@dataclass
class RiskThresholds:
    expiry_med_pct: float = 25.0
    expiry_high_pct: float = 40.0
    concentration_med_pct: float = 20.0
    concentration_high_pct: float = 35.0
    caprate_diff_max: float = 0.03


DEFAULT_WEIGHTS = RiskWeights()
DEFAULT_THRESHOLDS = RiskThresholds()
