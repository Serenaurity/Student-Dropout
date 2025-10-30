import numpy as np
from typing import Dict, List, Optional, Tuple
import math

class FeatureEngineer:
    """
    Class สำหรับสร้าง features ที่จำเป็นสำหรับโมเดลจากข้อมูลพื้นฐาน
    """
    
    def __init__(self):
        # Faculty mapping
        self.faculty_mapping = {
            "วิทยาศาสตร์และเทคโนโลยี": 0,
            "วิศวกรรมศาสตร์": 1,
            "บริหารธุรกิจ": 2,
            "ศิลปศาสตร์": 3,
            "แพทยศาสตร์": 4,
            "อื่นๆ": 5
        }
        
        # Gender mapping
        self.gender_mapping = {
            "ชาย": 0,
            "หญิง": 1
        }
    
    def calculate_gpa_features(self, term_gpas: List[float]) -> Dict[str, float]:
        """
        คำนวณ features ที่เกี่ยวข้องกับ GPA
        """
        # กรองค่า None ออก
        valid_gpas = [gpa for gpa in term_gpas if gpa is not None]
        
        if not valid_gpas:
            return {
                'avg_gpa': 0.0,
                'min_gpa': 0.0,
                'max_gpa': 0.0,
                'gpa_std': 0.0,
                'gpa_trend': 0.0,
                'num_terms_completed': 0,
                'last_gpa': 0.0
            }
        
        avg_gpa = np.mean(valid_gpas)
        min_gpa = np.min(valid_gpas)
        max_gpa = np.max(valid_gpas)
        gpa_std = np.std(valid_gpas) if len(valid_gpas) > 1 else 0.0
        last_gpa = valid_gpas[-1]
        num_terms_completed = len(valid_gpas)
        
        # คำนวณ trend (เปรียบเทียบเทอมแรกกับเทอมสุดท้าย)
        if len(valid_gpas) >= 2:
            gpa_trend = valid_gpas[-1] - valid_gpas[0]
        else:
            gpa_trend = 0.0
        
        return {
            'avg_gpa': avg_gpa,
            'min_gpa': min_gpa,
            'max_gpa': max_gpa,
            'gpa_std': gpa_std,
            'gpa_trend': gpa_trend,
            'num_terms_completed': num_terms_completed,
            'last_gpa': last_gpa
        }
    
    def calculate_additional_features(self, term_gpas: List[float], count_f: int, gpax: float) -> Dict[str, float]:
        """
        คำนวณ features เพิ่มเติม
        """
        valid_gpas = [gpa for gpa in term_gpas if gpa is not None]
        
        # Features ที่เกี่ยวข้องกับ F
        has_f = 1 if count_f > 0 else 0
        multiple_f = 1 if count_f > 1 else 0
        
        # Features ที่เกี่ยวข้องกับ GPA levels
        low_gpa = 1 if gpax < 2.0 else 0
        very_low_gpa = 1 if gpax < 1.5 else 0
        
        # Features ที่เกี่ยวข้องกับ trend
        declining_trend = 0
        if len(valid_gpas) >= 3:
            recent_avg = np.mean(valid_gpas[-2:])
            earlier_avg = np.mean(valid_gpas[:-2])
            declining_trend = 1 if recent_avg < earlier_avg else 0
        
        # Early warning (GPA ต่ำ + มี F)
        early_warning = 1 if (gpax < 2.5 and count_f > 0) else 0
        
        # ส่งคืนทั้งรูปแบบชื่อที่โมเดลต้องการและแบบ lowercase ที่ UI ใช้
        return {
            'has_F': float(has_f),          # ชื่อตามโมเดล
            'multiple_F': float(multiple_f),# ชื่อตามโมเดล
            'has_f': has_f,                 # สำหรับคำอธิบาย UI
            'multiple_f': multiple_f,       # สำหรับคำอธิบาย UI
            'low_gpa': low_gpa,
            'very_low_gpa': very_low_gpa,
            'declining_trend': declining_trend,
            'early_warning': early_warning
        }
    
    def create_model_features(self, 
                            faculty: str,
                            gender: str,
                            gpax: float,
                            count_f: int,
                            term_gpas: List[Optional[float]],
                            current_term: int = 1) -> Dict[str, float]:
        """
        สร้าง features ทั้งหมดที่โมเดลต้องการ
        """
        # คำนวณ GPA features
        gpa_features = self.calculate_gpa_features(term_gpas)
        
        # คำนวณ additional features
        additional_features = self.calculate_additional_features(term_gpas, count_f, gpax)
        
        # เตรียมข้อมูลสำหรับแต่ละเทอม (TERM1-TERM8)
        term_features = {}
        for i in range(1, 9):
            term_key = f'TERM{i}'
            if i <= len(term_gpas) and term_gpas[i-1] is not None:
                term_features[term_key] = term_gpas[i-1]
            else:
                term_features[term_key] = 0.0
        
        # คำนวณ features เพิ่มเติมสำหรับ XGBoost models
        # Missing indicators
        term_missing_features = {}
        for i in range(1, 4):  # TERM1-TERM3 missing
            term_key = f'TERM{i}_missing'
            if i <= len(term_gpas):
                term_missing_features[term_key] = 1 if term_gpas[i-1] is None else 0
            else:
                term_missing_features[term_key] = 1
        
        # GPA change features
        gpa_change_features = {}
        if len([gpa for gpa in term_gpas if gpa is not None]) >= 2:
            valid_gpas = [gpa for gpa in term_gpas if gpa is not None]
            gpa_change_features['gpa_change_from_start'] = valid_gpas[-1] - valid_gpas[0]
            gpa_change_features['gpa_std_up_to_now'] = np.std(valid_gpas) if len(valid_gpas) > 1 else 0.0
        else:
            gpa_change_features['gpa_change_from_start'] = 0.0
            gpa_change_features['gpa_std_up_to_now'] = 0.0
        
        # Decline features
        decline_features = {}
        if len([gpa for gpa in term_gpas if gpa is not None]) >= 2:
            valid_gpas = [gpa for gpa in term_gpas if gpa is not None]
            recent_avg = np.mean(valid_gpas[-2:]) if len(valid_gpas) >= 2 else valid_gpas[-1]
            earlier_avg = np.mean(valid_gpas[:-2]) if len(valid_gpas) > 2 else valid_gpas[0]
            decline_features['decline_last_term'] = 1 if recent_avg < earlier_avg else 0
            decline_features['consecutive_decline_2'] = 1 if len(valid_gpas) >= 2 and valid_gpas[-1] < valid_gpas[-2] else 0
        else:
            decline_features['decline_last_term'] = 0
            decline_features['consecutive_decline_2'] = 0
        
        # สร้าง features ทั้งหมด
        features = {
            # Term features
            **term_features,
            
            # Missing indicators
            **term_missing_features,
            
            # Basic features
            'COUNT_F': float(count_f),
            'COUNT_WIU': 0.0,  # ยังไม่มีข้อมูล WIU
            'OLD_GPA_M6': gpax,  # ใช้ GPAX เป็น OLD_GPA_M6
            'avg_gpa_up_to_now': gpa_features['avg_gpa'],
            'min_gpa_up_to_now': gpa_features['min_gpa'],
            'max_gpa_up_to_now': gpa_features['max_gpa'],
            'improvement_from_hs': gpa_features['gpa_trend'],  # ใช้ gpa_trend เป็น improvement_from_hs
            
            # Encoded features
            'GENDER_ENCODED': float(self.gender_mapping.get(gender, 0)),
            'FAC_ENCODED': float(self.faculty_mapping.get(faculty, 0)),
            
            # Additional features
            **additional_features,
            
            # GPA change features
            **gpa_change_features,
            
            # Decline features
            **decline_features,
            
            # Current term
            'current_term': float(current_term)
        }
        
        return features
    
    def predict_future_scenario(self, 
                              current_features: Dict[str, float],
                              future_gpa: float,
                              current_term: int) -> Dict[str, float]:
        """
        ทำนายผลลัพธ์หากเกรดเทอมต่อไปเป็นตามที่กำหนด
        """
        # คัดลอก features ปัจจุบัน
        future_features = current_features.copy()
        
        # อัปเดต TERM สำหรับเทอมถัดไป
        next_term = current_term + 1
        if next_term <= 8:
            future_features[f'TERM{next_term}'] = future_gpa
        
        # อัปเดต features ที่เกี่ยวข้อง
        # คำนวณ GPA ใหม่
        term_gpas = []
        for i in range(1, 9):
            term_gpa = future_features.get(f'TERM{i}', 0.0)
            if term_gpa > 0:
                term_gpas.append(term_gpa)
        
        if term_gpas:
            future_features['GPA'] = np.mean(term_gpas)
            future_features['last_gpa'] = term_gpas[-1]
            future_features['num_terms_completed'] = len(term_gpas)
            
            # คำนวณ trend ใหม่
            if len(term_gpas) >= 2:
                future_features['gpa_trend'] = term_gpas[-1] - term_gpas[0]
        
        return future_features
    
    def get_feature_explanation(self, features: Dict[str, float]) -> Dict[str, str]:
        """
        อธิบายความหมายของ features ที่สำคัญ
        """
        explanations = {}
        
        # GPA related
        if features.get('GPA', 0) > 0:
            explanations['GPA'] = f"เกรดเฉลี่ยสะสม: {features['GPA']:.2f}"
        
        if features.get('gpa_trend', 0) != 0:
            trend_desc = "เพิ่มขึ้น" if features['gpa_trend'] > 0 else "ลดลง"
            explanations['gpa_trend'] = f"แนวโน้มเกรด: {trend_desc} {abs(features['gpa_trend']):.2f}"
        
        # F related
        if features.get('COUNT_F', 0) > 0:
            explanations['COUNT_F'] = f"จำนวนวิชาที่ได้ F: {int(features['COUNT_F'])} วิชา"
        
        if features.get('has_f', 0) == 1:
            explanations['has_f'] = "มีประวัติได้เกรด F"
        
        # Risk indicators
        if features.get('early_warning', 0) == 1:
            explanations['early_warning'] = "มีสัญญาณเตือน: เกรดต่ำและมี F"
        
        if features.get('declining_trend', 0) == 1:
            explanations['declining_trend'] = "แนวโน้มเกรดลดลง"
        
        return explanations
