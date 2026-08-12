from pydantic import BaseModel


class AnomalyAlert(BaseModel):
    date: str
    metric: str
    value: float
    z_score: float
    modified_z_score: float
    iqr_outlier: bool
    percent_change: float
    severity: str


class AnomalyPoint(BaseModel):
    date: str
    value: float
    anomaly: bool
    severity: str
