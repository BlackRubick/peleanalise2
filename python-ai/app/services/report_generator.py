"""
Professional PDF report generator using ReportLab.
"""

import io
import base64
from datetime import datetime
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image as RLImage, HRFlowable,
)


BRAND_BLUE   = colors.HexColor("#4f46e5")
BRAND_GRAY   = colors.HexColor("#6b7280")
RISK_COLORS  = {
    "BENIGNO":    colors.HexColor("#10b981"),
    "SOSPECHOSO": colors.HexColor("#f59e0b"),
    "MALIGNO":    colors.HexColor("#ef4444"),
}


def generate_pdf(study_data: dict[str, Any], image_b64: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title", parent=styles["Title"],
        textColor=BRAND_BLUE, fontSize=18, spaceAfter=6,
    )
    heading_style = ParagraphStyle(
        "Heading", parent=styles["Heading2"],
        textColor=BRAND_BLUE, fontSize=12, spaceBefore=12, spaceAfter=4,
    )
    label_style = ParagraphStyle(
        "Label", parent=styles["Normal"],
        textColor=BRAND_GRAY, fontSize=8,
    )
    value_style = ParagraphStyle(
        "Value", parent=styles["Normal"],
        fontSize=10, fontName="Helvetica-Bold",
    )

    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    story.append(Paragraph("PeleAnálise", title_style))
    story.append(Paragraph("Reporte de Análisis Dermatológico", styles["Normal"]))
    story.append(HRFlowable(width="100%", color=BRAND_BLUE, thickness=1.5, spaceAfter=12))

    # ── Patient info ─────────────────────────────────────────────────────────
    p = study_data.get("patient", {})
    story.append(Paragraph("Datos del Paciente", heading_style))

    patient_table_data = [
        [Paragraph("Nombre", label_style),
         Paragraph(f"{p.get('firstName','')} {p.get('lastName','')}", value_style),
         Paragraph("Fecha nacimiento", label_style),
         Paragraph(str(p.get("birthDate", "—"))[:10], value_style)],
        [Paragraph("Sexo", label_style),
         Paragraph(str(p.get("sex", "—")), value_style),
         Paragraph("CURP", label_style),
         Paragraph(str(p.get("curp", "—")), value_style)],
    ]
    pt = Table(patient_table_data, colWidths=[3 * cm, 5.5 * cm, 3 * cm, 5.5 * cm])
    pt.setStyle(TableStyle([
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(pt)

    # ── Study info ──────────────────────────────────────────────────────────
    story.append(Paragraph("Datos del Estudio", heading_style))
    study_date = str(study_data.get("studyDate", ""))[:10]

    study_info = Table([
        [Paragraph("Fecha", label_style), Paragraph(study_date, value_style),
         Paragraph("Localización", label_style), Paragraph(str(study_data.get("anatomicLocation", "—")), value_style)],
        [Paragraph("Tipo de lesión", label_style), Paragraph(str(study_data.get("lesionType", "—")), value_style),
         Paragraph("Médico", label_style), Paragraph(f"{study_data.get('capturedBy', {}).get('firstName', '')} {study_data.get('capturedBy', {}).get('lastName', '')}", value_style)],
    ], colWidths=[3 * cm, 5.5 * cm, 3 * cm, 5.5 * cm])
    story.append(study_info)

    # ── Images ──────────────────────────────────────────────────────────────
    story.append(Paragraph("Imágenes del Estudio", heading_style))
    img_row = []
    for img_type, b64 in image_b64.items():
        if not b64:
            continue
        try:
            img_data = base64.b64decode(b64)
            img_buf  = io.BytesIO(img_data)
            img      = RLImage(img_buf, width=5 * cm, height=5 * cm)
            img_row.append([img, Paragraph(img_type, label_style)])
        except Exception:
            pass

    if img_row:
        img_table = Table([img_row[:3]], colWidths=[6 * cm] * min(len(img_row), 3))
        img_table.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
        story.append(img_table)

    # ── ABCDE ───────────────────────────────────────────────────────────────
    analysis = study_data.get("analysis", {})
    abcde    = analysis.get("abcde", {})
    if abcde:
        story.append(Paragraph("Análisis ABCDE", heading_style))
        rows = [
            ["Criterio", "Score", "Detalles"],
            ["A — Asimetría",  f"{abcde.get('asymmetryScore', 0):.3f}", f"H: {abcde.get('asymmetryH',0):.3f}  V: {abcde.get('asymmetryV',0):.3f}"],
            ["B — Bordes",     f"{abcde.get('borderScore', 0):.3f}",    f"Compacidad: {abcde.get('compactness',0):.3f}  Rugosidad: {abcde.get('rugosity',0):.3f}"],
            ["C — Color",      f"{abcde.get('colorScore', 0):.3f}",     f"Varianza cromática: {abcde.get('colorVariance',0):.3f}"],
            ["D — Diámetro",   f"{abcde.get('diameterMm', 0):.2f} mm",  f"Píxeles: {abcde.get('diameterPx',0):.1f}"],
            ["TOTAL",          f"{abcde.get('totalScore', 0):.3f}",     ""],
        ]
        t = Table(rows, colWidths=[5 * cm, 3 * cm, 9 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0), BRAND_BLUE),
            ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f9fafb")]),
            ("BACKGROUND",  (0, -1), (-1, -1), colors.HexColor("#e0e7ff")),
            ("FONTNAME",    (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t)

    # ── AI Prediction ────────────────────────────────────────────────────────
    prediction = analysis.get("prediction", {})
    if prediction:
        story.append(Paragraph("Predicción de Inteligencia Artificial", heading_style))
        risk  = str(prediction.get("prediction", "")).upper()
        color = RISK_COLORS.get(risk, BRAND_GRAY)

        pred_style = ParagraphStyle(
            "Pred", parent=styles["Normal"],
            fontSize=20, fontName="Helvetica-Bold", textColor=color,
        )
        story.append(Paragraph(prediction.get("prediction", "—"), pred_style))
        story.append(Paragraph(
            f"Probabilidad: {round(float(prediction.get('probability', 0)) * 100)}% · "
            f"Modelo v{prediction.get('modelVersion', '—')}",
            styles["Normal"],
        ))

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", color=BRAND_GRAY, thickness=0.5))
    story.append(Paragraph(
        f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} · PeleAnálise v1.0 · "
        "Este reporte es una herramienta de apoyo clínico. No reemplaza el juicio médico profesional.",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=7, textColor=BRAND_GRAY),
    ))

    doc.build(story)
    return buffer.getvalue()
