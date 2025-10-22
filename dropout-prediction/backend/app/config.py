from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Dropout Prediction API"
    VERSION: str = "1.0.0"
    MODEL_PATH: str = "ml_models/xgboost_dropout_tuned_model.json"
    DEBUG: bool = True
    
    class Config:
        case_sensitive = True

settings = Settings()
