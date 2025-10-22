from fastapi import APIRouter
from ....models.schemas import HealthResponse
from ....models.ml_model import predictor

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy" if predictor.model_loaded else "unhealthy",
        model_loaded=predictor.model_loaded
    )