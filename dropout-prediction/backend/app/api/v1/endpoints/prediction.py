from fastapi import APIRouter, HTTPException
from ....models.schemas import StudentInput, StudentBasicInput, PredictionOutput, FuturePredictionRequest, FuturePredictionOutput
from ....models.ml_model import predictor
from ....utils.feature_engineering import FeatureEngineer

router = APIRouter()
feature_engineer = FeatureEngineer()

@router.post("/predict", response_model=PredictionOutput)
async def predict(student: StudentInput):
    """ทำนายจาก features ที่ประมวลผลแล้ว"""
    if not predictor.model_loaded:
        raise HTTPException(503, "Model not loaded")
    
    data = student.model_dump()
    pred, prob = predictor.predict(data)
    risk, color = predictor.get_risk(prob)
    
    return PredictionOutput(
        prediction=pred,
        prediction_label="Dropout" if pred == 1 else "Graduate",
        dropout_probability=prob,
        dropout_percentage=f"{prob*100:.1f}%",
        risk_level=risk,
        risk_color=color,
        recommendation=f"Risk level: {risk}"
    )

@router.post("/predict-from-basic", response_model=PredictionOutput)
async def predict_from_basic(student_basic: StudentBasicInput):
    """ทำนายจากข้อมูลพื้นฐาน"""
    if not predictor.model_loaded:
        raise HTTPException(503, "Model not loaded")
    
    try:
        # แปลงข้อมูลพื้นฐานเป็น term GPAs
        term_gpas = [
            student_basic.year1_term1,
            student_basic.year1_term2,
            student_basic.year2_term1,
            student_basic.year2_term2,
            student_basic.year3_term1,
            student_basic.year3_term2,
            student_basic.year4_term1,
            student_basic.year4_term2,
            student_basic.year5_term1,
            student_basic.year5_term2
        ]
        
        # สร้าง features
        features = feature_engineer.create_model_features(
            faculty=student_basic.faculty,
            gender=student_basic.gender,
            gpax=student_basic.gpax,
            count_f=student_basic.count_f,
            term_gpas=term_gpas
        )
        
        # ทำนาย
        pred, prob = predictor.predict(features, num_terms=len([gpa for gpa in term_gpas if gpa is not None]))
        risk, color = predictor.get_risk(prob)
        
        # สร้างคำแนะนำ
        recommendation = generate_recommendation(risk, prob, features)
        
        # อธิบาย features ที่สำคัญ
        feature_explanations = feature_engineer.get_feature_explanation(features)
        
        return PredictionOutput(
            prediction=pred,
            prediction_label="Dropout" if pred == 1 else "Graduate",
            dropout_probability=prob,
            dropout_percentage=f"{prob*100:.1f}%",
            risk_level=risk,
            risk_color=color,
            recommendation=recommendation,
            feature_explanations=feature_explanations
        )
        
    except Exception as e:
        raise HTTPException(400, f"Error processing data: {str(e)}")

@router.post("/predict-future", response_model=FuturePredictionOutput)
async def predict_future(request: FuturePredictionRequest):
    """ทำนายผลลัพธ์หากเกรดเทอมถัดไปเป็นตามที่กำหนด"""
    if not predictor.model_loaded:
        raise HTTPException(503, "Model not loaded")
    
    try:
        # แปลงข้อมูลพื้นฐานเป็น term GPAs
        term_gpas = [
            request.year1_term1,
            request.year1_term2,
            request.year2_term1,
            request.year2_term2,
            request.year3_term1,
            request.year3_term2,
            request.year4_term1,
            request.year4_term2,
            request.year5_term1,
            request.year5_term2
        ]
        
        # สร้าง features ปัจจุบัน
        current_features = feature_engineer.create_model_features(
            faculty=request.faculty,
            gender=request.gender,
            gpax=request.gpax,
            count_f=request.count_f,
            term_gpas=term_gpas
        )
        
        # คำนวณเทอมปัจจุบัน
        current_term = len([gpa for gpa in term_gpas if gpa is not None])
        
        # สร้าง features สำหรับอนาคต
        future_features = feature_engineer.predict_future_scenario(
            current_features, request.future_gpa, current_term
        )
        
        # ทำนายทั้งสองกรณี
        current_num_terms = len([gpa for gpa in term_gpas if gpa is not None])
        current_pred, current_prob = predictor.predict(current_features, num_terms=current_num_terms)
        future_pred, future_prob = predictor.predict(future_features, num_terms=current_num_terms + 1)
        
        # คำนวณการปรับปรุง
        improvement = current_prob - future_prob
        improvement_percentage = f"{improvement*100:.1f}%"
        
        # สร้างคำแนะนำ
        if improvement > 0:
            recommendation = f"หากได้เกรด {request.future_gpa:.2f} ในเทอมถัดไป ความเสี่ยงจะลดลง {improvement_percentage}"
        elif improvement < 0:
            recommendation = f"หากได้เกรด {request.future_gpa:.2f} ในเทอมถัดไป ความเสี่ยงจะเพิ่มขึ้น {abs(improvement)*100:.1f}%"
        else:
            recommendation = f"หากได้เกรด {request.future_gpa:.2f} ในเทอมถัดไป ความเสี่ยงจะไม่เปลี่ยนแปลง"
        
        return FuturePredictionOutput(
            current_probability=current_prob,
            future_probability=future_prob,
            current_percentage=f"{current_prob*100:.1f}%",
            future_percentage=f"{future_prob*100:.1f}%",
            improvement=improvement,
            improvement_percentage=improvement_percentage,
            recommendation=recommendation
        )
        
    except Exception as e:
        raise HTTPException(400, f"Error processing future prediction: {str(e)}")

def generate_recommendation(risk_level: str, probability: float, features: dict) -> str:
    """สร้างคำแนะนำตามระดับความเสี่ยง"""
    recommendations = []
    
    if risk_level == "High":
        recommendations.append("⚠️ ความเสี่ยงสูง: ควรปรึกษาอาจารย์ที่ปรึกษาทันที")
        if features.get('COUNT_F', 0) > 0:
            recommendations.append("📚 ควรปรับปรุงการเรียนในวิชาที่ได้ F")
        if features.get('gpa_trend', 0) < 0:
            recommendations.append("📈 ควรหาวิธีปรับปรุงเกรดให้ดีขึ้น")
    elif risk_level == "Medium":
        recommendations.append("⚠️ ความเสี่ยงปานกลาง: ควรปรับพฤติกรรมการเรียน")
        recommendations.append("📖 หมั่นทบทวนบทเรียนและเข้าชั้นเรียนอย่างสม่ำเสมอ")
        recommendations.append("⏰ จัดตารางอ่านหนังสือและพักผ่อนให้เพียงพอ")
    else:
        recommendations.append("✅ ความเสี่ยงต่ำ: ควรรักษาระดับการเรียนให้ดี")
        recommendations.append("🎯 ตั้งเป้าหมายและวางแผนการเรียนให้ชัดเจน")
    
    return " | ".join(recommendations)
