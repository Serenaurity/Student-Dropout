import xgboost as xgb
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
from ..config import settings
import time

class DropoutPredictor:
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.features = ['TERM1','TERM2','TERM3','TERM4','TERM5','TERM6','TERM7','TERM8',
                        'COUNT_F','COUNT_WIU','OLD_GPA_M6','GPA','num_terms_completed',
                        'last_gpa','gpa_trend','GENDER_ENCODED','FAC_ENCODED']
    
    def load_model(self, max_retries=3):
        for attempt in range(max_retries):
            try:
                path = Path(settings.MODEL_PATH)
                print(f"🔄 Attempt {attempt + 1}/{max_retries}")
                print(f"🔍 Looking for model at: {path}")
                print(f"📁 Absolute path: {path.absolute()}")
                print(f"✅ File exists: {path.exists()}")
                
                if path.exists():
                    print(f"📦 File size: {path.stat().st_size} bytes")
                    self.model = xgb.XGBClassifier()
                    self.model.load_model(str(path))
                    self.model_loaded = True
                    print(f"✅ Model loaded successfully!")
                    return True
                else:
                    print(f"❌ File not found")
                    
            except Exception as e:
                print(f"❌ Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ Waiting 2 seconds before retry...")
                    time.sleep(2)
                else:
                    print(f"❌ Failed to load model after {max_retries} attempts")
                    import traceback
                    traceback.print_exc()
        
        return False
    
    def predict(self, data: Dict) -> Tuple[int, float]:
        if not self.model_loaded:
            # Try to load model again
            print("⚠️ Model not loaded, attempting to load...")
            if not self.load_model():
                raise RuntimeError("Model not loaded and failed to reload")
        
        features = [float(data.get(f, 0) or 0) for f in self.features]
        X = np.array([features])
        pred = self.model.predict(X)[0]
        prob = self.model.predict_proba(X)[0, 1]
        return int(pred), float(prob)
    
    def get_risk(self, prob):
        if prob < 0.3: 
            return "Low", "green"
        elif prob < 0.6: 
            return "Medium", "orange"
        else: 
            return "High", "red"

predictor = DropoutPredictor()