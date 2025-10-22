from fastapi import APIRouter, HTTPException
from ....models.schemas import StudentInput, PredictionOutput
from ....models.ml_model import predictor

router = APIRouter()

@router.post("/predict", response_model=PredictionOutput)
async def predict(student: StudentInput):
    if not predictor.model_loaded:
        raise HTTPException(503, "Model not loaded")
    
    data = student.model_dump()
    pred, prob = predictor.predict(data)
    risk, color = predictor.get_risk(prob)
    
    return PredictionOutput(
        prediction=pred,
        prediction_label="Dropout" if pred == 1 else "Graduate",
        dropout_probability=prob,
        dropout_percentage=f"{prob*100:.2f}%",
        risk_level=risk,
        risk_color=color,
        recommendation=f"Risk level: {risk}"
    )
