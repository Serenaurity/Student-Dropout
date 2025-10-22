from fastapi import APIRouter
from .endpoints import health, prediction

router = APIRouter()
router.include_router(health.router, tags=["Health"])
router.include_router(prediction.router, tags=["Prediction"])
