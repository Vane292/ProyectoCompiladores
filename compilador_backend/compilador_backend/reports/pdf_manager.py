# ============================================================
#  compilador_backend/reports/pdf_manager.py  —  REEMPLAZA el archivo actual
# ============================================================
import os
import tempfile
from datetime import datetime

# ── Intentamos importar reportlab (preferido) o fpdf2 ───────
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table,
        TableStyle, HRFlowable
    )
    _ENGINE = "reportlab"
except ImportError:
    try:
        from fpdf import FPDF
        _ENGINE = "fpdf"
    except ImportError:
        _ENGINE = None


# ── Función pública ───────────────────────────────────────────
def generar_reporte_pdf(codigo: str, resultado: dict) -> str:
    """
    Genera un PDF con el reporte completo del análisis del compilador.
    Retorna la ruta absoluta del archivo generado.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre    = f"reporte_compilador_{timestamp}.pdf"
    ruta      = os.path.join(tempfile.gettempdir(), nombre)

    if _ENGINE == "reportlab":
        _generar_con_reportlab(ruta, codigo, resultado)
    elif _ENGINE == "fpdf":
        _generar_con_fpdf(ruta, codigo, resultado)
    else:
        # Fallback: genera un PDF mínimo con bytes válidos (texto plano encapsulado)
        _generar_fallback(ruta, codigo, resultado)

    return ruta


# ── Implementación con ReportLab ─────────────────────────────
def _generar_con_reportlab(ruta: str, codigo: str, resultado: dict):
    doc    = SimpleDocTemplate(ruta, pagesize=A4,
                               topMargin=2*cm, bottomMargin=2*cm,
                               leftMargin=2*cm, rightMargin=2*cm)
    estilos = getSampleStyleSheet()
    historia = []

    # Paleta de colores
    AZUL_OSCURO = colors.HexColor("#0D1117")
    AZUL_MED    = colors.HexColor("#161B22")
    PLASMA      = colors.HexColor("#58A6FF")
    VERDE       = colors.HexColor("#3FB950")
    ROJO        = colors.HexColor("#F85149")
    GRIS        = colors.HexColor("#8B949E")
    BLANCO      = colors.white

    # Estilos personalizados
    estilo_titulo = ParagraphStyle("titulo",
        parent=estilos["Heading1"],
        fontSize=22, textColor=PLASMA,
        spaceAfter=6, fontName="Helvetica-Bold")

    estilo_subtitulo = ParagraphStyle("subtitulo",
        parent=estilos["Heading2"],
        fontSize=13, textColor=PLASMA,
        spaceBefore=14, spaceAfter=4, fontName="Helvetica-Bold")

    estilo_normal = ParagraphStyle("normal",
        parent=estilos["Normal"],
        fontSize=9, textColor=colors.HexColor("#C9D1D9"),
        leading=14)

    estilo_code = ParagraphStyle("code",
        parent=estilos["Code"],
        fontSize=8, textColor=colors.HexColor("#A5D6FF"),
        backColor=AZUL_OSCURO, leading=13,
        leftIndent=8, rightIndent=8,
        spaceBefore=4, spaceAfter=4)

    # ── Encabezado ──────────────────────────────────────────
    historia.append(Paragraph("COMPILE<font color='#58A6FF'>X</font> — Reporte de Análisis", estilo_titulo))
    historia.append(Paragraph(
        f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        ParagraphStyle("meta", parent=estilos["Normal"], fontSize=8, textColor=GRIS)
    ))
    historia.append(HRFlowable(width="100%", thickness=1, color=PLASMA, spaceAfter=10))

    # ── Veredicto ───────────────────────────────────────────
    valido        = resultado.get("overall_valid", False)
    color_verdict = VERDE if valido else ROJO
    texto_verdict = "✔ CÓDIGO VÁLIDO" if valido else "✘ CÓDIGO INVÁLIDO"

    historia.append(Paragraph(texto_verdict,
        ParagraphStyle("verdict", parent=estilos["Normal"],
            fontSize=16, textColor=color_verdict,
            fontName="Helvetica-Bold", spaceAfter=12)))

    # ── Código fuente ───────────────────────────────────────
    historia.append(Paragraph("Código Fuente Analizado", estilo_subtitulo))
    for linea in codigo.split("\n"):
        historia.append(Paragraph(
            linea.replace(" ", "&nbsp;").replace("<","&lt;").replace(">","&gt;") or "&nbsp;",
            estilo_code))
    historia.append(Spacer(1, 0.4*cm))

    # ── Fase 1: Léxico ──────────────────────────────────────
    historia.append(Paragraph("Fase 1 — Análisis Léxico", estilo_subtitulo))
    historia.append(HRFlowable(width="100%", thickness=0.5, color=PLASMA, spaceAfter=6))

    tokens = resultado.get("lexer", {}).get("tokens", [])
    if tokens:
        datos_tabla = [["#", "Tipo", "Valor", "Línea", "Col"]]
        for i, tok in enumerate(tokens[:60], 1):   # max 60 filas
            datos_tabla.append([
                str(i),
                tok.get("type", ""),
                str(tok.get("value", ""))[:30],
                str(tok.get("line", "")),
                str(tok.get("column", "")),
            ])
        tabla = Table(datos_tabla, colWidths=[1*cm, 3.5*cm, 5*cm, 1.5*cm, 1.5*cm])
        tabla.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,0), AZUL_MED),
            ("TEXTCOLOR",    (0,0), (-1,0), PLASMA),
            ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",     (0,0), (-1,-1), 7.5),
            ("BACKGROUND",   (0,1), (-1,-1), AZUL_OSCURO),
            ("TEXTCOLOR",    (0,1), (-1,-1), colors.HexColor("#C9D1D9")),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [AZUL_OSCURO, AZUL_MED]),
            ("GRID",         (0,0), (-1,-1), 0.3, colors.HexColor("#21262D")),
            ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING",   (0,0), (-1,-1), 3),
            ("BOTTOMPADDING",(0,0), (-1,-1), 3),
        ]))
        historia.append(tabla)

    # Errores léxicos
    errores_lex = resultado.get("lexer", {}).get("errors", [])
    if errores_lex:
        historia.append(Spacer(1, 0.3*cm))
        historia.append(Paragraph("Errores Léxicos:", ParagraphStyle("err_hdr",
            parent=estilos["Normal"], fontSize=9, textColor=ROJO, fontName="Helvetica-Bold")))
        for e in errores_lex:
            historia.append(Paragraph(f"• {e.get('message','')}", estilo_normal))

    # ── Fase 2: Sintáctico ──────────────────────────────────
    historia.append(Paragraph("Fase 2 — Análisis Sintáctico", estilo_subtitulo))
    historia.append(HRFlowable(width="100%", thickness=0.5, color=PLASMA, spaceAfter=6))

    parser_data = resultado.get("parser", {})
    estado_parser = "VÁLIDO ✔" if parser_data.get("valid") else "INVÁLIDO ✘"
    color_parser  = VERDE if parser_data.get("valid") else ROJO
    historia.append(Paragraph(f"Estado gramatical: <font color='{color_parser.hexval()}'>{estado_parser}</font>",
        ParagraphStyle("parser_est", parent=estilos["Normal"], fontSize=10, textColor=colors.HexColor("#C9D1D9"))))

    errores_par = parser_data.get("errors", [])
    if errores_par:
        historia.append(Spacer(1, 0.2*cm))
        for e in errores_par:
            historia.append(Paragraph(f"• Línea {e.get('line','?')}: {e.get('message','')}",
                ParagraphStyle("err", parent=estilos["Normal"], fontSize=8.5, textColor=ROJO)))

    # ── Fase 3: Semántico ───────────────────────────────────
    historia.append(Paragraph("Fase 3 — Análisis Semántico", estilo_subtitulo))
    historia.append(HRFlowable(width="100%", thickness=0.5, color=PLASMA, spaceAfter=6))

    semantic_data = resultado.get("semantic", {})
    simbolos      = semantic_data.get("symbol_table", [])

    if simbolos:
        historia.append(Paragraph("Tabla de Símbolos:", ParagraphStyle("sym_hdr",
            parent=estilos["Normal"], fontSize=9, textColor=GRIS, spaceAfter=4)))
        datos_sym = [["Nombre", "Tipo", "Valor", "Ámbito"]]
        for s in simbolos:
            datos_sym.append([s.get("name",""), s.get("type",""), str(s.get("value","")), s.get("scope","global")])

        tabla_sym = Table(datos_sym, colWidths=[4*cm, 3*cm, 5*cm, 3.5*cm])
        tabla_sym.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,0), AZUL_MED),
            ("TEXTCOLOR",    (0,0), (-1,0), PLASMA),
            ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",     (0,0), (-1,-1), 8),
            ("BACKGROUND",   (0,1), (-1,-1), AZUL_OSCURO),
            ("TEXTCOLOR",    (0,1), (-1,-1), colors.HexColor("#C9D1D9")),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [AZUL_OSCURO, AZUL_MED]),
            ("GRID",         (0,0), (-1,-1), 0.3, colors.HexColor("#21262D")),
            ("TOPPADDING",   (0,0), (-1,-1), 3),
            ("BOTTOMPADDING",(0,0), (-1,-1), 3),
        ]))
        historia.append(tabla_sym)

    errores_sem = semantic_data.get("errors", [])
    if errores_sem:
        historia.append(Spacer(1, 0.3*cm))
        for e in errores_sem:
            historia.append(Paragraph(f"• {e.get('message','')}",
                ParagraphStyle("err2", parent=estilos["Normal"], fontSize=8.5, textColor=ROJO)))

    # ── Pie ─────────────────────────────────────────────────
    historia.append(Spacer(1, 0.6*cm))
    historia.append(HRFlowable(width="100%", thickness=0.5, color=GRIS))
    historia.append(Paragraph("Generado por CompileX · Compilador Web",
        ParagraphStyle("footer", parent=estilos["Normal"], fontSize=7,
            textColor=GRIS, alignment=1, spaceBefore=4)))

    doc.build(historia)


# ── Implementación con FPDF2 (fallback) ──────────────────────
def _generar_con_fpdf(ruta: str, codigo: str, resultado: dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Título
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(88, 166, 255)
    pdf.cell(0, 10, "CompileX - Reporte de Analisis", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(110, 118, 129)
    pdf.cell(0, 6, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True)
    pdf.ln(4)

    # Veredicto
    valido = resultado.get("overall_valid", False)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(63, 185, 80) if valido else pdf.set_text_color(248, 81, 73)
    pdf.cell(0, 10, "CODIGO VALIDO" if valido else "CODIGO INVALIDO", ln=True)
    pdf.ln(3)

    # Código fuente
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(88, 166, 255)
    pdf.cell(0, 8, "Codigo Fuente:", ln=True)
    pdf.set_font("Courier", "", 8)
    pdf.set_text_color(201, 209, 217)
    for linea in codigo.split("\n"):
        pdf.cell(0, 5, linea[:100], ln=True)
    pdf.ln(4)

    # Tokens
    tokens = resultado.get("lexer", {}).get("tokens", [])
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(88, 166, 255)
    pdf.cell(0, 8, f"Fase 1 - Lexico ({len(tokens)} tokens):", ln=True)
    pdf.set_font("Courier", "", 7.5)
    pdf.set_text_color(201, 209, 217)
    for tok in tokens[:50]:
        pdf.cell(0, 4.5, f"  {tok.get('type',''):<18} '{tok.get('value','')}' L{tok.get('line','')}", ln=True)
    pdf.ln(3)

    # Tabla de símbolos
    simbolos = resultado.get("semantic", {}).get("symbol_table", [])
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(88, 166, 255)
    pdf.cell(0, 8, "Fase 3 - Tabla de Simbolos:", ln=True)
    pdf.set_font("Courier", "", 8)
    pdf.set_text_color(201, 209, 217)
    for s in simbolos:
        pdf.cell(0, 5, f"  {s.get('name',''):<15} tipo: {s.get('type',''):<8} valor: {s.get('value','')}", ln=True)

    # Errores
    todos_errores = (
        resultado.get("lexer", {}).get("errors", []) +
        resultado.get("parser", {}).get("errors", []) +
        resultado.get("semantic", {}).get("errors", [])
    )
    if todos_errores:
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(248, 81, 73)
        pdf.cell(0, 8, "Errores detectados:", ln=True)
        pdf.set_font("Helvetica", "", 8.5)
        for e in todos_errores:
            pdf.cell(0, 5, f"  * {e.get('message','')[:100]}", ln=True)

    pdf.output(ruta)


# ── Fallback mínimo sin dependencias ─────────────────────────
def _generar_fallback(ruta: str, codigo: str, resultado: dict):
    """
    Genera un PDF válido mínimo usando solo bytes puros.
    Solo se usa si no hay reportlab ni fpdf instalados.
    """
    valido  = resultado.get("overall_valid", False)
    tokens  = resultado.get("lexer", {}).get("tokens", [])
    errores = (
        resultado.get("lexer", {}).get("errors", []) +
        resultado.get("parser", {}).get("errors", []) +
        resultado.get("semantic", {}).get("errors", [])
    )

    lineas_pdf = [
        "COMPILEX - REPORTE DE ANALISIS",
        f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        "",
        f"RESULTADO: {'CODIGO VALIDO' if valido else 'CODIGO INVALIDO'}",
        "",
        "CODIGO FUENTE:",
        *[f"  {l}" for l in codigo.split("\n")[:30]],
        "",
        f"TOKENS ({len(tokens)}):",
        *[f"  {t.get('type')}: '{t.get('value')}' L{t.get('line')}" for t in tokens[:40]],
        "",
        "ERRORES:" if errores else "Sin errores detectados.",
        *[f"  * {e.get('message','')}" for e in errores],
    ]

    contenido = "\n".join(lineas_pdf)
    # PDF texto plano mínimo válido
    objetos = []
    objetos.append(b"%PDF-1.4\n")
    offsets = []

    def obj(n, contenido_obj):
        offsets.append(len(b"".join(objetos)))
        objetos.append(f"{n} 0 obj\n{contenido_obj}\nendobj\n".encode())

    obj(1, "<< /Type /Catalog /Pages 2 0 R >>")

    texto_escapado = contenido.replace("\\","\\\\").replace("(","\\(").replace(")","\\)")
    texto_bt = f"BT /F1 9 Tf 40 780 Td 14 TL ({texto_escapado}) Tj ET"
    obj(3, f"<< /Length {len(texto_bt)} >>\nstream\n{texto_bt}\nendstream")
    obj(4, "<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")
    obj(5, f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 3 0 R /Resources << /Font << /F1 4 0 R >> >> >>")
    obj(2, "<< /Type /Pages /Kids [5 0 R] /Count 1 >>")

    xref_offset = len(b"".join(objetos))
    objetos.append(b"xref\n")
    objetos.append(f"0 {len(offsets)+1}\n".encode())
    objetos.append(b"0000000000 65535 f \n")
    for off in offsets:
        objetos.append(f"{off:010d} 00000 n \n".encode())
    objetos.append(b"trailer\n")
    objetos.append(f"<< /Size {len(offsets)+1} /Root 1 0 R >>\n".encode())
    objetos.append(b"startxref\n")
    objetos.append(f"{xref_offset}\n".encode())
    objetos.append(b"%%EOF\n")

    with open(ruta, "wb") as f:
        f.write(b"".join(objetos))