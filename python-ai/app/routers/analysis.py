import base64
import numpy as np
import cv2

from fastapi import APIRouter, HTTPException
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse, ProcessedImages
from app.services.image_processing import full_pipeline
from app.services.abcde import compute_abcde
from app.services.ai_model import predict, generate_gradcam
from app.core.config import settings

router = APIRouter(prefix="/analyze", tags=["analysis"])


def decode_image(image_base64: str) -> np.ndarray:
    try:
        img_bytes = base64.b64decode(image_base64)
        arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("imdecode returned None")
        return img
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Imagen inválida o corrupta: {e}")


@router.post("", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    # 1. Decode image from base64 (sent directly by Nuxt — no HTTP round-trip)
    image_bgr = decode_image(req.image_base64)

    # 2. Preprocessing pipeline
    processed = full_pipeline(image_bgr)

    # 3. ABCDE metrics
    ppm   = req.pixel_per_mm or settings.PIXEL_PER_MM
    abcde = compute_abcde(processed["original"], processed["mask"], pixel_per_mm=ppm)

    # 4. AI prediction
    result = predict(processed["cleaned"])

    # 5. Grad-CAM
    gradcam_img = generate_gradcam(processed["cleaned"])

    # 6. (Optional) save processed images
    processed_images = ProcessedImages()

    return AnalyzeResponse(
        prediccion=result["prediccion"],
        probabilidad=result["probabilidad"],
        prob_benigno=result["prob_benigno"],
        prob_sospechoso=result["prob_sospechoso"],
        prob_maligno=result["prob_maligno"],
        model_version=result["model_version"],
        inference_time_ms=result["inference_time_ms"],
        abcde=abcde,
        processed_images=processed_images,
    )
