"""
ABCDE dermoscopy rule calculator.
All metrics derived from the binary lesion mask + original color image.
"""

import cv2
import numpy as np
from app.schemas.analysis import (
    AsymmetryMetrics, BorderMetrics, ColorMetrics,
    DiameterMetrics, ABCDEResult,
)


# ── A: Asymmetry ──────────────────────────────────────────────────────────────

def compute_asymmetry(mask: np.ndarray) -> AsymmetryMetrics:
    m = cv2.moments(mask)
    if m["m00"] == 0:
        return AsymmetryMetrics(score=0, h=0, v=0, hu_moments=[0.0] * 7)

    # Centroid
    cx = int(m["m10"] / m["m00"])
    cy = int(m["m01"] / m["m00"])

    # Flip and XOR for asymmetry score
    flipped_h = cv2.flip(mask, 1)  # horizontal flip
    flipped_v = cv2.flip(mask, 0)  # vertical flip

    xor_h = cv2.bitwise_xor(mask, flipped_h)
    xor_v = cv2.bitwise_xor(mask, flipped_v)

    area  = float(np.sum(mask > 0))
    h_diff = float(np.sum(xor_h > 0)) / (area + 1e-6)
    v_diff = float(np.sum(xor_v > 0)) / (area + 1e-6)
    score  = (h_diff + v_diff) / 2.0

    hu = cv2.HuMoments(m).flatten().tolist()
    return AsymmetryMetrics(score=score, h=h_diff, v=v_diff, hu_moments=hu)


# ── B: Border ─────────────────────────────────────────────────────────────────

def compute_border(mask: np.ndarray) -> BorderMetrics:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return BorderMetrics(score=0, perimeter=0, area=0, compactness=0, rugosity=0)

    cnt = max(contours, key=cv2.contourArea)
    perimeter = cv2.arcLength(cnt, True)
    area      = cv2.contourArea(cnt)

    compactness = (perimeter ** 2) / (4 * np.pi * area + 1e-6)

    # Rugosity: ratio convex hull perimeter vs actual perimeter
    hull      = cv2.convexHull(cnt)
    hull_peri = cv2.arcLength(hull, True)
    rugosity  = perimeter / (hull_peri + 1e-6)

    # Score: normalize compactness (1=circle, >1=irregular)
    score = min((compactness - 1.0) / 3.0, 1.0)

    return BorderMetrics(
        score=float(score),
        perimeter=float(perimeter),
        area=float(area),
        compactness=float(compactness),
        rugosity=float(rugosity),
    )


# ── C: Color ──────────────────────────────────────────────────────────────────

def compute_color(image_bgr: np.ndarray, mask: np.ndarray) -> ColorMetrics:
    roi = image_bgr[mask > 0]  # pixels inside lesion
    if len(roi) == 0:
        return ColorMetrics(score=0, variance=0, mean_r=0, mean_g=0, mean_b=0,
                            std_r=0, std_g=0, std_b=0, histogram=[])

    b, g, r = roi[:, 0], roi[:, 1], roi[:, 2]
    mean_r, mean_g, mean_b = float(r.mean()), float(g.mean()), float(b.mean())
    std_r,  std_g,  std_b  = float(r.std()),  float(g.std()),  float(b.std())
    variance = float((std_r + std_g + std_b) / 3.0)

    # Histogram (combined RGB, 32 bins)
    hist, _ = np.histogram(roi.flatten(), bins=32, range=(0, 256))
    histogram = (hist / hist.sum()).tolist()

    # Score: higher color variance → higher risk
    score = min(variance / 80.0, 1.0)

    return ColorMetrics(
        score=float(score),
        variance=variance,
        mean_r=mean_r, mean_g=mean_g, mean_b=mean_b,
        std_r=std_r,  std_g=std_g,   std_b=std_b,
        histogram=histogram,
    )


# ── D: Diameter ───────────────────────────────────────────────────────────────

def compute_diameter(mask: np.ndarray, pixel_per_mm: float = 25.4) -> DiameterMetrics:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return DiameterMetrics(score=0, diameter_px=0, diameter_mm=0, pixel_per_mm=pixel_per_mm)

    cnt = max(contours, key=cv2.contourArea)
    _, _, w, h = cv2.boundingRect(cnt)
    diameter_px = float(max(w, h))
    diameter_mm = diameter_px / pixel_per_mm

    # ABCDE criterion: ≥ 6mm is concerning
    score = min(diameter_mm / 12.0, 1.0)

    return DiameterMetrics(
        score=float(score),
        diameter_px=diameter_px,
        diameter_mm=float(diameter_mm),
        pixel_per_mm=float(pixel_per_mm),
    )


# ── Full ABCDE ─────────────────────────────────────────────────────────────────

def compute_abcde(
    image_bgr: np.ndarray,
    mask: np.ndarray,
    pixel_per_mm: float = 25.4,
) -> ABCDEResult:
    a = compute_asymmetry(mask)
    b = compute_border(mask)
    c = compute_color(image_bgr, mask)
    d = compute_diameter(mask, pixel_per_mm)

    # Weighted ABCDE score (clinical weights)
    total = (
        a.score * 1.3 +
        b.score * 0.1 +
        c.score * 0.5 +
        d.score * 0.5
    )

    return ABCDEResult(
        asymmetry=a,
        border=b,
        color=c,
        diameter=d,
        total_score=float(total),
    )
