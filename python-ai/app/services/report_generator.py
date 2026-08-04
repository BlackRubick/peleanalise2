"""
Professional PDF report generator — black & white, properly aligned.
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

# ── Paleta estricta B&W ────────────────────────────────────────────────────────
C_BLACK      = colors.HexColor("#000000")
C_DARK       = colors.HexColor("#1a1a1a")
C_MID        = colors.HexColor("#555555")
C_LIGHT_RULE = colors.HexColor("#cccccc")
C_ROW_ALT    = colors.HexColor("#f4f4f4")
C_ROW_TOTAL  = colors.HexColor("#e0e0e0")
C_WHITE      = colors.white

# ── Dimensiones ────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4
MARGIN  = 2.2 * cm
CW      = PAGE_W - 2 * MARGIN          # ancho exacto del contenido


def _make_styles():
    b = getSampleStyleSheet()
    def ps(name, **kw):
        return ParagraphStyle(name, parent=b["Normal"], **kw)

    return {
        "title":    ps("T",  fontName="Helvetica-Bold",  fontSize=20, leading=26, textColor=C_BLACK, spaceAfter=4),
        "subtitle": ps("Su", fontName="Helvetica",       fontSize=9,  leading=13, textColor=C_MID,   spaceAfter=4),
        "sec_hdr":  ps("SH", fontName="Helvetica-Bold",  fontSize=9,  leading=13, textColor=C_WHITE),
        "label":    ps("L",  fontName="Helvetica",       fontSize=8,  leading=11, textColor=C_MID),
        "value":    ps("V",  fontName="Helvetica-Bold",  fontSize=9,  leading=13, textColor=C_DARK),
        "normal":   ps("N",  fontName="Helvetica",       fontSize=9,  leading=13, textColor=C_DARK),
        "risk":     ps("R",  fontName="Helvetica-Bold",  fontSize=18, leading=24, textColor=C_BLACK),
        "pct":      ps("P",  fontName="Helvetica-Bold",  fontSize=13, leading=18, textColor=C_DARK),
        "footer":   ps("F",  fontName="Helvetica",       fontSize=7,  leading=10, textColor=C_MID),
    }


def _section(story, title, st):
    """Encabezado de sección: barra negra con texto blanco."""
    t = Table(
        [[Paragraph(title.upper(), st["sec_hdr"])]],
        colWidths=[CW],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_BLACK),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    story.append(Spacer(1, 0.35 * cm))
    story.append(t)
    story.append(Spacer(1, 0.15 * cm))


def _data_table(rows_data, col_w, st):
    """
    rows_data: lista de [(lbl1, val1, lbl2, val2), ...]
    Devuelve tabla alineada con CW exacto.
    """
    data = []
    for row in rows_data:
        if len(row) == 4:
            lbl1, val1, lbl2, val2 = row
            data.append([
                Paragraph(lbl1, st["label"]),
                Paragraph(str(val1), st["value"]),
                Paragraph(lbl2, st["label"]),
                Paragraph(str(val2), st["value"]),
            ])
        elif len(row) == 2:
            lbl1, val1 = row
            data.append([
                Paragraph(lbl1, st["label"]),
                Paragraph(str(val1), st["value"]),
                Paragraph("", st["label"]),
                Paragraph("", st["value"]),
            ])

    t = Table(data, colWidths=col_w)
    t.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.3, C_LIGHT_RULE),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [C_WHITE, C_ROW_ALT]),
    ]))
    return t


def generate_pdf(study_data: dict[str, Any], image_b64: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=MARGIN, leftMargin=MARGIN,
        topMargin=2 * cm,   bottomMargin=2 * cm,
    )
    st    = _make_styles()
    story = []

    # Anchos de columna para tablas de 4 col (lbl‑val‑lbl‑val)
    LBL_W = CW * 0.22
    VAL_W = CW * 0.28
    col4  = [LBL_W, VAL_W, LBL_W, VAL_W]   # suma = CW exacto

    # ── Encabezado ───────────────────────────────────────────────────────────
    story.append(Paragraph("PeleAnálise", st["title"]))
    story.append(Paragraph("Reporte de Análisis Dermatológico", st["subtitle"]))
    story.append(Spacer(1, 0.25 * cm))
    story.append(HRFlowable(width="100%", color=C_BLACK, thickness=2, spaceAfter=3))
    story.append(Paragraph(
        f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y   %H:%M  hrs')}",
        st["footer"],
    ))

    # ── Paciente ─────────────────────────────────────────────────────────────
    p      = study_data.get("patient", {})
    nombre = f"{p.get('firstName','')  } {p.get('lastName','')}".strip() or "—"

    _section(story, "Datos del Paciente", st)
    story.append(_data_table([
        ("Nombre completo",    nombre,
         "Fecha de nacimiento", str(p.get("birthDate","—"))[:10]),
        ("Sexo",               str(p.get("sex","—")),
         "CURP",               str(p.get("curp","—"))),
        ("Teléfono",           str(p.get("phone","—")),
         "Correo electrónico", str(p.get("email","—"))),
    ], col4, st))

    # ── Estudio ──────────────────────────────────────────────────────────────
    medico = (
        f"{study_data.get('capturedBy',{}).get('firstName','')} "
        f"{study_data.get('capturedBy',{}).get('lastName','')}".strip() or "—"
    )
    _section(story, "Datos del Estudio", st)
    story.append(_data_table([
        ("Fecha del estudio",     str(study_data.get("studyDate",""))[:10],
         "Localización anatómica", str(study_data.get("anatomicLocation","—"))),
        ("Tipo de lesión",        str(study_data.get("lesionType","—")),
         "Médico responsable",    medico),
    ], col4, st))

    comments = str(study_data.get("clinicalComments","") or "").strip()
    if comments:
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph("Comentarios clínicos:", st["label"]))
        story.append(Paragraph(comments, st["normal"]))

    # ── Imágenes ─────────────────────────────────────────────────────────────
    img_cells = []
    for img_type, b64 in image_b64.items():
        if not b64:
            continue
        try:
            raw = base64.b64decode(b64)
            img = RLImage(io.BytesIO(raw), width=4.5 * cm, height=4.5 * cm)
            lbl = Paragraph(img_type.replace("_", " ").title(), st["label"])
            img_cells.append((img, lbl))
        except Exception:
            pass

    if img_cells:
        _section(story, "Imágenes del Estudio", st)
        n_cols  = 3
        img_col = CW / n_cols
        # Rellena hasta múltiplo de 3
        while len(img_cells) % n_cols:
            img_cells.append((Paragraph("", st["label"]), Paragraph("", st["label"])))

        for i in range(0, len(img_cells), n_cols):
            chunk = img_cells[i:i + n_cols]
            img_row = [c[0] for c in chunk]
            lbl_row = [c[1] for c in chunk]
            it = Table([img_row, lbl_row], colWidths=[img_col] * n_cols)
            it.setStyle(TableStyle([
                ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING",    (0, 0), (-1, -1), 4),
                ("BOX",           (0, 0), (-1, -1), 0.4, C_LIGHT_RULE),
                ("INNERGRID",     (0, 0), (-1, -1), 0.3, C_LIGHT_RULE),
            ]))
            story.append(it)

    # ── ABCDE ────────────────────────────────────────────────────────────────
    analysis = study_data.get("analysis", {})
    abcde    = analysis.get("abcde", {})
    if abcde:
        _section(story, "Análisis ABCDE", st)

        # Anchos: criterio 35%, score 18%, detalles 47%
        aw = [CW * 0.35, CW * 0.18, CW * 0.47]

        def th(txt):
            return Paragraph(txt, ParagraphStyle(
                "ATH", parent=st["sec_hdr"], fontSize=8))

        rows = [
            [th("Criterio"), th("Score"), th("Detalles")],
            ["A — Asimetría",
             f"{abcde.get('asymmetryScore',0):.3f}",
             f"Horizontal: {abcde.get('asymmetryH',0):.3f}   Vertical: {abcde.get('asymmetryV',0):.3f}"],
            ["B — Bordes",
             f"{abcde.get('borderScore',0):.3f}",
             f"Compacidad: {abcde.get('compactness',0):.3f}   Rugosidad: {abcde.get('rugosity',0):.3f}"],
            ["C — Color",
             f"{abcde.get('colorScore',0):.3f}",
             f"Varianza cromática: {abcde.get('colorVariance',0):.3f}"],
            ["D — Diámetro",
             f"{abcde.get('diameterMm',0):.2f} mm",
             f"Diámetro en píxeles: {abcde.get('diameterPx',0):.1f}"],
            ["TOTAL",
             f"{abcde.get('totalScore',0):.3f}",
             ""],
        ]

        at = Table(rows, colWidths=aw)
        at.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1,  0), C_BLACK),
            ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS",(0, 1), (-1, -2), [C_WHITE, C_ROW_ALT]),
            ("BACKGROUND",    (0, -1),(-1, -1), C_ROW_TOTAL),
            ("FONTNAME",      (0, -1),(-1, -1), "Helvetica-Bold"),
            ("GRID",          (0, 0), (-1, -1), 0.4, C_LIGHT_RULE),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 7),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(KeepTogether(at))

    # ── Predicción IA ─────────────────────────────────────────────────────────
    prediction = analysis.get("prediction", {})
    if prediction:
        _section(story, "Predicción de Inteligencia Artificial", st)

        risk    = str(prediction.get("prediction", "")).upper()
        labels  = {"BENIGNO": "BENIGNO", "SOSPECHOSO": "SOSPECHOSO", "MALIGNO": "MALIGNO"}
        lbl_tx  = labels.get(risk, risk)
        prob    = round(float(prediction.get("probability",  0)) * 100)
        p_ben   = round(float(prediction.get("probBenigno",  0)) * 100)
        p_sos   = round(float(prediction.get("probSospechoso", 0)) * 100)
        p_mal   = round(float(prediction.get("probMaligno",  0)) * 100)
        version = str(prediction.get("modelVersion", "—"))

        # Fila principal: resultado + probabilidad principal
        def th2(txt):
            return Paragraph(txt, ParagraphStyle(
                "PTH", parent=st["sec_hdr"], fontSize=8))

        pred_t = Table(
            [
                [th2("Resultado IA"), th2("Probabilidad"), th2("Versión del modelo")],
                [Paragraph(lbl_tx, st["risk"]),
                 Paragraph(f"{prob}%", st["pct"]),
                 Paragraph(version, st["value"])],
            ],
            colWidths=[CW * 0.40, CW * 0.25, CW * 0.35],
        )
        pred_t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), C_BLACK),
            ("BACKGROUND",    (0, 1), (-1, 1), C_ROW_ALT),
            ("GRID",          (0, 0), (-1, -1), 0.4, C_LIGHT_RULE),
            ("TOPPADDING",    (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(pred_t)

        # Distribución de probabilidades por clase
        story.append(Spacer(1, 0.25 * cm))
        prob_t = Table(
            [
                [th2("Benigno"), th2("Sospechoso"), th2("Maligno")],
                [Paragraph(f"{p_ben}%", st["value"]),
                 Paragraph(f"{p_sos}%", st["value"]),
                 Paragraph(f"{p_mal}%", st["value"])],
            ],
            colWidths=[CW / 3, CW / 3, CW / 3],
        )
        prob_t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0), C_BLACK),
            ("ROWBACKGROUNDS",(0, 1), (-1, 1), [C_WHITE]),
            ("GRID",          (0, 0), (-1, -1), 0.4, C_LIGHT_RULE),
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(prob_t)

    # ── Pie de página ─────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.8 * cm))
    story.append(HRFlowable(width="100%", color=C_LIGHT_RULE, thickness=0.5, spaceAfter=4))
    story.append(Paragraph(
        "AVISO IMPORTANTE: Este reporte es una herramienta de apoyo clínico generada de forma automática. "
        "No sustituye el diagnóstico ni el criterio del médico profesional tratante.",
        st["footer"],
    ))
    story.append(Paragraph(
        f"PeleAnálise v1.0  ·  {datetime.now().strftime('%d/%m/%Y  %H:%M  hrs')}",
        st["footer"],
    ))

    doc.build(story)
    return buffer.getvalue()
