import xgboost as xgb
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
from ..config import settings
import time
import os

class DropoutPredictor:
    def __init__(self):
        self.models = {
            'term1': None,
            'term2': None, 
            'term3': None
        }
        self.model_loaded = False
        self.model_paths = {
            'term1': 'XG/model_term1.json',
            'term2': 'XG/model_term2.json',
            'term3': 'XG/model_term3.json'
        }
        
        # Features สำหรับแต่ละ model
        self.features = {
            'term1': ['OLD_GPA_M6','GENDER_ENCODED','FAC_ENCODED','COUNT_F','COUNT_WIU','TERM1','TERM1_missing','avg_gpa_up_to_now','min_gpa_up_to_now','max_gpa_up_to_now','improvement_from_hs','has_F','multiple_F','low_gpa','early_warning','current_term'],
            'term2': ['OLD_GPA_M6','GENDER_ENCODED','FAC_ENCODED','COUNT_F','COUNT_WIU','TERM1','TERM1_missing','TERM2','TERM2_missing','avg_gpa_up_to_now','min_gpa_up_to_now','max_gpa_up_to_now','gpa_change_from_start','gpa_std_up_to_now','decline_last_term','improvement_from_hs','has_F','multiple_F','low_gpa','early_warning','current_term'],
            'term3': ['OLD_GPA_M6','GENDER_ENCODED','FAC_ENCODED','COUNT_F','COUNT_WIU','TERM1','TERM1_missing','TERM2','TERM2_missing','TERM3','TERM3_missing','avg_gpa_up_to_now','min_gpa_up_to_now','max_gpa_up_to_now','gpa_change_from_start','gpa_std_up_to_now','decline_last_term','consecutive_decline_2','improvement_from_hs','has_F','multiple_F','low_gpa','early_warning','current_term']
        }
    
    def load_models(self, max_retries=3):
        """โหลด models ทั้งหมด"""
        loaded_count = 0
        
        for term, model_path in self.model_paths.items():
            for attempt in range(max_retries):
                try:
                    # สร้าง absolute path
                    abs_path = Path(__file__).parent.parent.parent.parent / model_path
                    print(f"🔄 Loading {term} model - Attempt {attempt + 1}/{max_retries}")
                    print(f"🔍 Looking for model at: {abs_path}")
                    print(f"✅ File exists: {abs_path.exists()}")
                    
                    if abs_path.exists():
                        print(f"📦 File size: {abs_path.stat().st_size} bytes")
                        self.models[term] = xgb.XGBClassifier()
                        self.models[term].load_model(str(abs_path))
                        loaded_count += 1
                        print(f"✅ {term} model loaded successfully!")
                        break
                    else:
                        print(f"❌ File not found: {abs_path}")
                        
                except Exception as e:
                    print(f"❌ Error loading {term} model on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        print(f"⏳ Waiting 2 seconds before retry...")
                        time.sleep(2)
                    else:
                        print(f"❌ Failed to load {term} model after {max_retries} attempts")
                        import traceback
                        traceback.print_exc()
        
        if loaded_count > 0:
            self.model_loaded = True
            print(f"✅ Successfully loaded {loaded_count}/3 models")
            return True
        else:
            print(f"❌ Failed to load any models")
            return False
    
    def get_model_for_term(self, num_terms: int) -> str:
        """เลือก model ตามจำนวนเทอมที่เรียนแล้ว"""
        if num_terms == 1:
            return 'term1'
        elif num_terms == 2:
            return 'term2'
        else:  # 3 เทอมขึ้นไป
            return 'term3'
    
    def predict(self, data: Dict, num_terms: int = None) -> Tuple[int, float]:
        """ทำนายผลลัพธ์"""
        if not self.model_loaded:
            print("⚠️ Models not loaded, attempting to load...")
            if not self.load_models():
                raise RuntimeError("Models not loaded and failed to reload")
        
        # เลือก model ตามจำนวนเทอม
        if num_terms is None:
            # คำนวณจำนวนเทอมจากข้อมูล
            term_count = 0
            for i in range(1, 9):
                if data.get(f'TERM{i}', 0) > 0:
                    term_count += 1
            num_terms = term_count
        
        model_key = self.get_model_for_term(num_terms)
        model = self.models[model_key]
        
        if model is None:
            raise RuntimeError(f"Model {model_key} not loaded")
        
        print(f"🎯 Using {model_key} model for {num_terms} terms")
        
        # เตรียม features สำหรับ model ที่เลือก
        model_features = self.features[model_key]
        features = []
        
        for feature in model_features:
            value = data.get(feature, 0)
            if isinstance(value, (int, float)):
                features.append(float(value))
            else:
                features.append(0.0)
        
        X = np.array([features])
        pred = model.predict(X)[0]
        prob = model.predict_proba(X)[0, 1]
        
        return int(pred), float(prob)
    
    def get_risk(self, prob):
        """ประเมินระดับความเสี่ยง"""
        if prob < 0.3: 
            return "Low", "green"
        elif prob < 0.6: 
            return "Medium", "orange"
        else: 
            return "High", "red"

predictor = DropoutPredictor()