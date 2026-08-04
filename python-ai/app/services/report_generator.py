"""
Professional PDF report generator using ReportLab — black & white design.
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
    Image as RLImage, HRFlowable, KeepTogether,
)

BLACK      = colors.HexColor("#000000")
DARK_GRAY  = colors.HexColor("#333333")
MID_GRAY   = colors.HexColor("#666666")
LIGHT_GRAY = colors.HexColor("#f2f2f2")
RULE_GRAY  = colors.HexColor("#cccccc")
WHITE      = colors.white

RISK_LABEL = {
    "BENIGNO":    "BENIGNO",
    "SOSPECHOSO": "SOSPECHOSO",
    "MALIGNO":    "MALIGNO",
}


def _styles():
    base = getSampleStyleSheet()

    title = ParagraphStyle(
        "RPTitle",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=BLACK,
        spaceAfter=2,
    )
    subtitle = ParagraphStyle(
        "RPSubtitle",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=MID_GRAY,
        spaceAfter=0,
    )
    section = ParagraphStyle(
        "RPSection",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=BLACK,
        spaceBefore=14,
        spaceAfter=5,
        borderPad=0,
    )
    label = ParagraphStyle(
        "RPLabel",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=8,
        textColor=MID_GRAY,
    )
    value = ParagraphStyle(
        "RPValue",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=BLACK,
    )
    normal = ParagraphStyle(
        "RPNormal",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=DARK_GRAY,
    )
    footer = ParagraphStyle(
        "RPFooter",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=7,
        textColor=MID_GRAY,
    )
    risk_big = ParagraphStyle(
        "RPRisk",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        textColor=BLACK,
        spaceAfter=2,
    )
    return dict(
        title=title, subtitle=subtitle, section=section,
        label=label, value=value, normal=normal,
        footer=footer, risk_big=risk_big,
    )


def _section_rule(story, title_text, s):
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(title_text.upper(), s["section"]))
    story.append(HRFlowable(width="100%", color=RULE_GRAY, thickness=0.5, spaceAfter=6))


def _info_table(rows, s, col_widths=None):
    """2-column label/value table."""
    if col_widths is None:
        col_widths = [3.5 * cm, 6 * cm, 3.5 * cm, 4 * cm]
    data = [
        [Paragraph(lbl1, s["label"]), Paragraph(val1, s["value"]),
         Paragraph(lbl2, s["label"]), Paragraph(val2, s["value"])]
        for lbl1, val1, lbl2, val2 in rows
    ]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.3, RULE_GRAY),
    ]))
    return t


def generate_pdf(study_data: dict[str, Any], image_b64: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2.2 * cm,
        leftMargin=2.2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    s = _styles()
    story = []

    # ── Header ──────────────────────────────────────────────────────────────────
    story.append(Paragraph("PeleAnálise", s["title"]))
    story.append(Paragraph("Reporte de Análisis Dermatológico", s["subtitle"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", color=BLACK, thickness=1.5, spaceAfter=4))
    story.append(Paragraph(
        f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y  %H:%M')}",
        s["footer"],
    ))

    # ── Datos del paciente ───────────────────────────────────────────────────────
    p = study_data.get("patient", {})
    nombre = f"{p.get('firstName', '')} {p.get('lastName', '')}".strip() or "—"
    nacimiento = str(p.get("birthDate", "—"))[:10]
    sexo = str(p.get("sex", "—"))
    curp = str(p.get("curp", "—"))
    telefono = str(p.get("phone", "—"))
    email = str(p.get("email", "—"))

    _section_rule(story, "Datos del Paciente", s)
    story.append(_info_table([
        ("Nombre completo", nombre,       "Fecha de nacimiento", nacimiento),
        ("Sexo",            sexo,         "CURP",                curp),
        ("Teléfono",        telefono,     "Correo",              email),
    ], s))

    # ── Datos del estudio ───────────────────────────────────────────────────────
    study_date = str(study_data.get("studyDate", ""))[:10]
    location   = str(study_data.get("anatomicLocation", "—"))
    lesion     = str(study_data.get("lesionType", "—"))
    medico     = f"{study_data.get('capturedBy', {}).get('firstName', '')} {study_data.get('capturedBy', {}).get('lastName', '')}".strip() or "—"
    comments   = str(study_data.get("clinicalComments", "—") or "—")

    _section_rule(story, "Datos del Estudio", s)
    story.append(_info_table([
        ("Fecha del estudio",  study_date, "Localización anatómica", location),
        ("Tipo de lesión",     lesion,     "Médico responsable",     medico),
    ], s))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Comentarios clínicos:", s["label"]))
    story.append(Paragraph(comments, s["normal"]))

    # ── Imágenes ────────────────────────────────────────────────────────────────
    img_items = []
    for img_type, b64 in image_b64.items():
        if not b64:
            continue
        try:
            img_data = base64.b64decode(b64)
            img_buf  = io.BytesIO(img_data)
            img      = RLImage(img_buf, width=4.8 * cm, height=4.8 * cm)
            label_p  = Paragraph(img_type.replace("_", " ").title(), s["label"])
            img_items.append([img, label_p])
        except Exception:
            pass

    if img_items:
        _section_rule(story, "Imágenes del Estudio", s)
        n = min(len(img_items), 3)
        row_imgs  = [cell[0] for cell in img_items[:n]]
        row_lbls  = [cell[1] for cell in img_items[:n]]
        pad = n
        while len(row_imgs) < 3:
            row_imgs.append(Paragraph("", s["label"]))
            row_lbls.append(Paragraph("", s["label"]))

        img_table = Table(
            [row_imgs, row_lbls],
            colWidths=[5.5 * cm, 5.5 * cm, 5.5 * cm],
        )
        img_table.setStyle(TableStyle([
            ("ALIGN",          (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
            ("BOX",            (0, 0), (pad - 1, 0), 0.5, RULE_GRAY),
        ]))
        story.append(img_table)

    # ── ABCDE ───────────────────────────────────────────────────────────────────
    analysis = study_data.get("analysis", {})
    abcde    = analysis.get("abcde", {})
    if abcde:
        _section_rule(story, "Análisis ABCDE", s)

        header_style = ParagraphStyle(
            "TH", parent=s["value"], textColor=WHITE, fontSize=9,
        )
        rows = [
            [Paragraph("Criterio",  header_style),
             Paragraph("Score",     header_style),
             Paragraph("Detalles",  header_style)],
            ["A — Asimetría",
             f"{abcde.get('asymmetryScore', 0):.3f}",
             f"Horizontal: {abcde.get('asymmetryH', 0):.3f}   Vertical: {abcde.get('asymmetryV', 0):.3f}"],
            ["B — Bordes",
             f"{abcde.get('borderScore', 0):.3f}",
             f"Compacidad: {abcde.get('compactness', 0):.3f}   Rugosidad: {abcde.get('rugosity', 0):.3f}"],
            ["C — Color",
             f"{abcde.get('colorScore', 0):.3f}",
             f"Varianza cromática: {abcde.get('colorVariance', 0):.3f}"],
            ["D — Diámetro",
             f"{abcde.get('diameterMm', 0):.2f} mm",
             f"Diámetro en píxeles: {abcde.get('diameterPx', 0):.1f}"],
            ["TOTAL",
             f"{abcde.get('totalScore', 0):.3f}",
             ""],
        ]

        t = Table(rows, colWidths=[5 * cm, 3 * cm, 9 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  BLACK),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS",(0, 1), (-1, -2), [WHITE, LIGHT_GRAY]),
            ("BACKGROUND",    (0, -1), (-1, -1), colors.HexColor("#e0e0e0")),
            ("FONTNAME",      (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID",          (0, 0), (-1, -1),  0.4, RULE_GRAY),
            ("BOTTOMPADDING", (0, 0), (-1, -1),  5),
            ("TOPPADDING",    (0, 0), (-1, -1),  4),
            ("LEFTPADDING",   (0, 0), (-1, -1),  6),
        ]))
        story.append(KeepTogether(t))

    # ── Predicción IA ────────────────────────────────────────────────────────────
    prediction = analysis.get("prediction", {})
    if prediction:
        _section_rule(story, "Predicción de Inteligencia Artificial", s)

        risk     = str(prediction.get("prediction", "")).upper()
        label_tx = RISK_LABEL.get(risk, risk)
        prob     = round(float(prediction.get("probability", 0)) * 100)
        version  = prediction.get("modelVersion", "—")

        pred_rows = [
            [Paragraph("Resultado", s["label"]),
             Paragraph("Probabilidad", s["label"]),
             Paragraph("Versión del modelo", s["label"])],
            [Paragraph(label_tx, s["risk_big"]),
             Paragraph(f"{prob}%", s["risk_big"]),
             Paragraph(str(version), s["value"])],
        ]
        pred_table = Table(pred_rows, colWidths=[6 * cm, 4 * cm, 7 * cm])
        pred_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  BLACK),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  WHITE),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, 0),  8),
            ("BACKGROUND",    (0, 1), (-1, 1),  LIGHT_GRAY),
            ("GRID",          (0, 0), (-1, -1), 0.4, RULE_GRAY),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ]))
        story.append(pred_table)

        # Distribución de probabilidades
        story.append(Spacer(1, 0.4 * cm))
        prob_rows = [
            [Paragraph("Benigno", s["label"]),
             Paragraph("Sospechoso", s["label"]),
             Paragraph("Maligno", s["label"])],
            [Paragraph(f"{round(float(prediction.get('probBenigno', 0)) * 100)}%", s["value"]),
             Paragraph(f"{round(float(prediction.get('probSospechoso', 0)) * 100)}%", s["value"]),
             Paragraph(f"{round(float(prediction.get('probMaligno', 0)) * 100)}%", s["value"])],
        ]
        prob_table = Table(prob_rows, colWidths=[5.6 * cm, 5.6 * cm, 5.6 * cm])
        prob_table.setStyle(TableStyle([
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("GRID",          (0, 0), (-1, -1), 0.4, RULE_GRAY),
            ("ROWBACKGROUNDS",(0, 0), (-1, -1), [colors.HexColor("#f8f8f8"), WHITE]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ]))
        story.append(prob_table)

    # ── Aviso legal ──────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.8 * cm))
    story.append(HRFlowable(width="100%", color=RULE_GRAY, thickness=0.5, spaceAfter=4))
    story.append(Paragraph(
        "AVISO: Este reporte es una herramienta de apoyo clínico generada de forma automática. "
        "No reemplaza el diagnóstico ni el juicio del médico profesional tratante.",
        s["footer"],
    ))
    story.append(Paragraph(
        f"PeleAnálise v1.0  ·  Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}",
        s["footer"],
    ))

    doc.build(story)
    return buffer.getvalue()
