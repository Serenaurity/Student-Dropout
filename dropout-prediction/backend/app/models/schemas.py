from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StudentInput(BaseModel):
    TERM1: Optional[float] = Field(None, ge=0, le=4)
    TERM2: Optional[float] = Field(None, ge=0, le=4)
    TERM3: Optional[float] = None
    TERM4: Optional[float] = None
    TERM5: Optional[float] = None
    TERM6: Optional[float] = None
    TERM7: Optional[float] = None
    TERM8: Optional[float] = None
    COUNT_F: int = Field(..., ge=0)
    COUNT_WIU: int = Field(..., ge=0)
    OLD_GPA_M6: float = Field(..., ge=0, le=4)
    GPA: float = Field(..., ge=0, le=4)
    num_terms_completed: int = Field(..., ge=1, le=10)
    last_gpa: float = Field(..., ge=0, le=4)
    gpa_trend: float = Field(..., ge=-4, le=4)
    GENDER_ENCODED: int = Field(..., ge=0, le=1)
    FAC_ENCODED: int = Field(..., ge=0, le=5)

class PredictionOutput(BaseModel):
    prediction: int
    prediction_label: str
    dropout_probability: float
    dropout_percentage: str
    risk_level: str
    risk_color: str
    recommendation: str
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
