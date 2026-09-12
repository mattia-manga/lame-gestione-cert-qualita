# -*- coding: utf-8 -*-
"""
Genera una scheda PDF riepilogativa per un singolo Heat/Colata
a partire da un dizionario di dati estratti dai certificati.

Uso: modificare il dizionario `dati` in fondo al file e lanciare lo script.
Il PDF viene salvato in /mnt/user-data/outputs/
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.enums import TA_CENTER


def crea_scheda_heat(dati: dict, output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "SubtitleCustom",
        parent=styles["Normal"],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=12,
    )
    section_style = ParagraphStyle(
        "SectionCustom",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.HexColor("#1a3c6e"),
        spaceBefore=14,
        spaceAfter=6,
    )

    story = []

    # ---------- Titolo ----------
    story.append(Paragraph("CERTIFICATO MATERIALE — SCHEDA HEAT", title_style))
    heat_num = dati["generali"].get("Heat Number", "")
    story.append(Paragraph(f"Heat Number: {heat_num}", subtitle_style))

    # ---------- Dati generali ----------
    story.append(Paragraph("DATI GENERALI", section_style))
    ordine_generali = [
        "Heat Code", "Heat Number", "Product", "Forgia", "Acciaieria",
        "Grado Materiale", "Numero Certificato", "Data Cert. Acciaieria",
    ]
    righe_generali = [[k, dati["generali"].get(k, "") or ""] for k in ordine_generali]
    t_generali = Table(righe_generali, colWidths=[55 * mm, 120 * mm])
    t_generali.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef2f7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c9c9c9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_generali)

    # ---------- Proprietà chimiche ----------
    story.append(Paragraph("PROPRIETÀ CHIMICHE (%)", section_style))
    ordine_chimici = ["C", "Mn", "P", "S", "Si", "Cr", "Ni", "Mo", "Ti",
                       "Cu", "Nb", "Co", "V", "CE", "N", "Al", "Ca", "B"]
    chim = dati.get("chimiche", {})
    n_col = 6
    righe_chim = []
    riga_label, riga_val = [], []
    for i, el in enumerate(ordine_chimici, 1):
        riga_label.append(el)
        riga_val.append(chim.get(el, "") or "")
        if i % n_col == 0:
            righe_chim.append(riga_label)
            righe_chim.append(riga_val)
            riga_label, riga_val = [], []
    if riga_label:
        while len(riga_label) < n_col:
            riga_label.append("")
            riga_val.append("")
        righe_chim.append(riga_label)
        righe_chim.append(riga_val)

    col_w = 160 * mm / n_col
    t_chim = Table(righe_chim, colWidths=[col_w] * n_col)
    style_chim = [
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c9c9c9")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for r in range(0, len(righe_chim), 2):
        style_chim.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#eef2f7")))
        style_chim.append(("FONTNAME", (0, r), (-1, r), "Helvetica-Bold"))
    t_chim.setStyle(TableStyle(style_chim))
    story.append(t_chim)

    # ---------- Proprietà meccaniche ----------
    story.append(Paragraph("PROPRIETÀ MECCANICHE", section_style))
    ordine_mecc = [
        "Elongation", "Reduction Area", "Yield Strength", "Tensile Str.",
        "Hardness (HBW)", "Impact Test",
    ]
    mecc = dati.get("meccaniche", {})
    righe_mecc = [[k, mecc.get(k, "") or ""] for k in ordine_mecc]

    # Campi tubo, solo se presenti nel dizionario
    if "tubo" in dati:
        for k in ["Hydraulic Test", "Bending Test"]:
            righe_mecc.append([k, dati["tubo"].get(k, "") or ""])

    t_mecc = Table(righe_mecc, colWidths=[55 * mm, 120 * mm])
    t_mecc.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef2f7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c9c9c9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_mecc)

    story.append(Spacer(1, 10 * mm))
    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"], fontSize=7.5, textColor=colors.grey
    )
    story.append(Paragraph(
        "Scheda generata automaticamente da estrazione certificati forgia/acciaieria. "
        "I campi vuoti indicano dato non presente o non rilevato.",
        footer_style,
    ))

    doc.build(story)
    print(f"PDF creato: {output_path}")


if __name__ == "__main__":
    # ESEMPIO D'USO — sostituire con i dati realmente estratti dal certificato.
    # Chiavi obbligatorie in "generali": Heat Code, Heat Number, Product, Forgia,
    # Acciaieria, Grado Materiale, Numero Certificato, Data Cert. Acciaieria.
    # Chiavi in "chimiche": C, Mn, P, S, Si, Cr, Ni, Mo, Ti, Cu, Nb, Co, V, CE, N, Al, Ca, B.
    # Chiavi in "meccaniche": Elongation, Reduction Area, Yield Strength,
    # Tensile Str., Hardness (HBW), Impact Test.
    # Chiave opzionale "tubo" (solo per tubi): Hydraulic Test, Bending Test.
    # Tutti i campi non trovati vanno lasciati come stringa vuota "".
    dati = {
        "generali": {
            "Heat Code": "",
            "Heat Number": "",
            "Product": "",
            "Forgia": "",
            "Acciaieria": "",
            "Grado Materiale": "",
            "Numero Certificato": "",
            "Data Cert. Acciaieria": "",
        },
        "chimiche": {
            "C": "", "Mn": "", "P": "", "S": "", "Si": "",
            "Cr": "", "Ni": "", "Mo": "", "Ti": "", "Cu": "",
            "Nb": "", "Co": "", "V": "", "CE": "", "N": "",
            "Al": "", "Ca": "", "B": "",
        },
        "meccaniche": {
            "Elongation": "",
            "Reduction Area": "",
            "Yield Strength": "",
            "Tensile Str.": "",
            "Hardness (HBW)": "",
            "Impact Test": "",
        },
        # "tubo": {"Hydraulic Test": "", "Bending Test": ""},
    }

    crea_scheda_heat(dati, "/mnt/user-data/outputs/Scheda_Heat_ESEMPIO.pdf")
