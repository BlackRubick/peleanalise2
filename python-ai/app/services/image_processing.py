"""
Image preprocessing pipeline:
  1. DullRazor hair removal
  2. Illumination normalization
  3. Segmentation (Otsu thresholding)
"""

import cv2
import numpy as np


def remove_hair_dullrazor(image: np.ndarray) -> np.ndarray:
    """DullRazor algorithm for hair artifact removal."""
    gray    = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Black-hat morphological filter to detect thin structures (hair)
    kernel  = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    # Threshold to create hair mask
    _, hair_mask = cv2.threshold(blackhat, 10, 255, cv2.THRESH_BINARY)
    # Dilate mask slightly
    hair_mask = cv2.dilate(hair_mask, kernel, iterations=1)
    # Inpaint to fill hair regions
    cleaned = cv2.inpaint(image, hair_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    return cleaned


def normalize_illumination(image: np.ndarray) -> np.ndarray:
    """Normalize brightness and contrast using CLAHE on L channel."""
    lab   = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_eq  = clahe.apply(l)
    lab_eq = cv2.merge([l_eq, a, b])
    return cv2.cvtColor(lab_eq, cv2.COLOR_LAB2BGR)


def segment_lesion(image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Otsu thresholding on grayscale to create binary lesion mask.
    Returns (mask, masked_image).
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Morphological cleanup
    kernel  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask    = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask    = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel, iterations=1)

    # Keep largest contour (the lesion)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest  = max(contours, key=cv2.contourArea)
        clean    = np.zeros_like(mask)
        cv2.drawContours(clean, [largest], -1, 255, cv2.FILLED)
        mask = clean

    masked = cv2.bitwise_and(image, image, mask=mask)
    return mask, masked


def full_pipeline(image_bgr: np.ndarray) -> dict:
    """Run the full preprocessing pipeline. Returns processed images."""
    cleaned = remove_hair_dullrazor(image_bgr)
    normalized = normalize_illumination(cleaned)
    mask, masked = segment_lesion(normalized)
    return {
        "original":   image_bgr,
        "cleaned":    normalized,
        "mask":       mask,
        "masked":     masked,
    }
