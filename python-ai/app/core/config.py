from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "PeleAnálise AI Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    MODEL_PATH: str = "models/melanoma_classifier.keras"
    MODEL_VERSION: str = "1.0.0"
    IMG_SIZE: int = 128

    # MinIO / S3 (for saving processed images)
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "peleanalise"
    MINIO_USE_SSL: bool = False

    # Pixel-to-mm calibration (default: dermoscopy standard)
    PIXEL_PER_MM: float = 25.4

    class Config:
        env_file = ".env"


settings = Settings()
