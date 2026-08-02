from pydantic import BaseModel
from typing import Optional


class AnalyzeRequest(BaseModel):
    image_base64: str
    study_id: str
    pixel_per_mm: Optional[float] = None


class AsymmetryMetrics(BaseModel):
    score: float
    h: float
    v: float
    hu_moments: list[float]


class BorderMetrics(BaseModel):
    score: float
    perimeter: float
    area: float
    compactness: float
    rugosity: float


class ColorMetrics(BaseModel):
    score: float
    variance: float
    mean_r: float
    mean_g: float
    mean_b: float
    std_r: float
    std_g: float
    std_b: float
    histogram: list[float]


class DiameterMetrics(BaseModel):
    score: float
    diameter_px: float
    diameter_mm: float
    pixel_per_mm: float


class ABCDEResult(BaseModel):
    asymmetry: AsymmetryMetrics
    border: BorderMetrics
    color: ColorMetrics
    diameter: DiameterMetrics
    total_score: float


class ProcessedImages(BaseModel):
    cleaned_path: Optional[str] = None
    mask_path: Optional[str] = None
    gradcam_path: Optional[str] = None


class AnalyzeResponse(BaseModel):
    prediccion: str
    probabilidad: float
    prob_benigno: float
    prob_sospechoso: float
    prob_maligno: float
    model_version: str
    inference_time_ms: int
    abcde: ABCDEResult
    processed_images: ProcessedImages
