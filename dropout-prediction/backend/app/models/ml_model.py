import xgboost as xgb
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
from ..config import settings

class DropoutPredictor:
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.features = ['TERM1','TERM2','TERM3','TERM4','TERM5','TERM6','TERM7','TERM8',
                        'COUNT_F','COUNT_WIU','OLD_GPA_M6','GPA','num_terms_completed',
                        'last_gpa','gpa_trend','GENDER_ENCODED','FAC_ENCODED']
    
    def load_model(self):
        try:
            path = Path(settings.MODEL_PATH)
            if path.exists():
                self.model = xgb.XGBClassifier()
                self.model.load_model(str(path))
                self.model_loaded = True
                print(f"Model loaded from {path}")
                return True
            else:
                print(f"Model not found at {path}")
        except Exception as e:
            print(f"Model load error: {e}")
        return False
    
    def predict(self, data: Dict) -> Tuple[int, float]:
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