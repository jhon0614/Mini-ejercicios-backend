from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfgen import canvas
from datetime import datetime
import os


# ──────────────────────────────────────────────
#  Paleta de colores
# ──────────────────────────────────────────────
COLOR_PRIMARIO   = colors.HexColor("#1F4E79")   # Azul oscuro
COLOR_SECUNDARIO = colors.HexColor("#2E75B6")   # Azul medio
COLOR_ACENTO     = colors.HexColor("#D6E4F0")   # Azul muy claro (fondo tabla)
COLOR_TEXTO      = colors.HexColor("#1A1A1A")
COLOR_GRIS       = colors.HexColor("#6B6B6B")
COLOR_LINEA      = colors.HexColor("#BDD7EE")


# ──────────────────────────────────────────────
#  Canvas personalizado: encabezado y pie fijos
# ──────────────────────────────────────────────
class FacturaCanvas(canvas.Canvas):
    """Agrega encabezado con nombre de empresa y pie de página en cada hoja."""

    def __init__(self, *args, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.empresa = empresa or {}
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_header_footer(total_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def _draw_header_footer(self, total_pages):
        self.saveState()
        w, h = letter

        # ── Encabezado ──
        self.setFillColor(COLOR_PRIMARIO)
        self.rect(0, h - 1.1 * inch, w, 1.1 * inch, fill=1, stroke=0)

        self.setFillColor(colors.white)
        self.setFont("Helvetica-Bold", 20)
        nombre_empresa = self.empresa.get("nombre", "Mi Empresa")
        self.drawString(0.5 * inch, h - 0.55 * inch, nombre_empresa)

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#BDD7EE"))
        info_linea1 = self.empresa.get("nit", "")
        info_linea2 = self.empresa.get("direccion", "")
        info_linea3 = self.empresa.get("telefono", "")
        self.drawRightString(w - 0.5 * inch, h - 0.35 * inch, info_linea1)
        self.drawRightString(w - 0.5 * inch, h - 0.50 * inch, info_linea2)
        self.drawRightString(w - 0.5 * inch, h - 0.65 * inch, info_linea3)

        # ── Pie de página ──
        self.setFillColor(COLOR_PRIMARIO)
        self.rect(0, 0, w, 0.45 * inch, fill=1, stroke=0)

        self.setFillColor(colors.white)
        self.setFont("Helvetica", 7)
        pie_texto = self.empresa.get("pie", "Gracias por su preferencia.")
        self.drawCentredString(w / 2, 0.17 * inch, pie_texto)

        self.setFont("Helvetica", 7)
        pagina_txt = f"Página {self._pageNumber} de {total_pages}"
        self.drawRightString(w - 0.5 * inch, 0.17 * inch, pagina_txt)

        self.restoreState()


# ──────────────────────────────────────────────
#  Función principal
# ──────────────────────────────────────────────
def generar_factura_pdf(
    output_path: str,
    numero_factura: str,
    fecha: str | None,
    cliente: dict,
    items: list[dict],
    empresa: dict | None = None,
    notas: str = "",
):
    """
    Genera una factura PDF profesional.

    Parámetros
    ----------
    output_path     : ruta donde se guarda el PDF (ej. "factura_001.pdf")
    numero_factura  : cadena como "FAC-2025-001"
    fecha           : "DD/MM/YYYY" o None (usa la fecha actual)
    cliente         : {"nombre": ..., "nit": ..., "direccion": ..., "email": ...}
    items           : lista de dicts con claves:
                        - descripcion  (str)
                        - cantidad     (int/float)
                        - precio_unit  (float)  — en pesos colombianos
                        - descuento    (float, opcional, porcentaje 0-100)
    empresa         : {"nombre": ..., "nit": ..., "direccion": ...,
                       "telefono": ..., "email": ..., "pie": ...}
    notas           : texto libre al pie de la factura
    """
    empresa = empresa or {
        "nombre": "Mi Empresa S.A.S.",
        "nit": "NIT: 900.123.456-7",
        "direccion": "Calle 50 #40-20, Medellín",
        "telefono": "Tel: +57 604 555 0000",
        "email": "facturacion@miempresa.com",
        "pie": "www.miempresa.com  |  facturacion@miempresa.com  |  +57 604 555 0000",
    }

    if fecha is None:
        fecha = datetime.now().strftime("%d/%m/%Y")

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=1.4 * inch,
        bottomMargin=0.7 * inch,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Estilos de texto ──
    estilo_titulo = ParagraphStyle(
        "titulo", fontSize=14, textColor=COLOR_PRIMARIO,
        fontName="Helvetica-Bold", spaceAfter=2
    )
    estilo_subtitulo = ParagraphStyle(
        "subtitulo", fontSize=9, textColor=COLOR_GRIS,
        fontName="Helvetica", spaceAfter=2
    )
    estilo_campo_label = ParagraphStyle(
        "campo_label", fontSize=8, textColor=COLOR_GRIS, fontName="Helvetica"
    )
    estilo_campo_valor = ParagraphStyle(
        "campo_valor", fontSize=9, textColor=COLOR_TEXTO, fontName="Helvetica-Bold"
    )
    estilo_nota = ParagraphStyle(
        "nota", fontSize=8, textColor=COLOR_GRIS, fontName="Helvetica", leading=12
    )

    # ── Bloque: Número de factura + datos cliente ──
    w_total = 7.5 * inch
    col_izq = 3.5 * inch
    col_der = 4.0 * inch

    encabezado_factura = [
        [
            # Columna izquierda — datos del cliente
            Table(
                [
                    [Paragraph("FACTURAR A:", estilo_campo_label)],
                    [Paragraph(cliente.get("nombre", "—"), estilo_campo_valor)],
                    [Paragraph(f"NIT / CC: {cliente.get('nit', '—')}", estilo_subtitulo)],
                    [Paragraph(cliente.get("direccion", ""), estilo_subtitulo)],
                    [Paragraph(cliente.get("email", ""), estilo_subtitulo)],
                ],
                colWidths=[col_izq],
                style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]),
            ),
            # Columna derecha — número y fecha
            Table(
                [
                    [Paragraph("FACTURA", estilo_titulo)],
                    [Paragraph(numero_factura, ParagraphStyle(
                        "num", fontSize=13, textColor=COLOR_SECUNDARIO,
                        fontName="Helvetica-Bold"
                    ))],
                    [Spacer(1, 6)],
                    [Paragraph("Fecha de emisión:", estilo_campo_label)],
                    [Paragraph(fecha, estilo_campo_valor)],
                ],
                colWidths=[col_der],
                style=TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN",  (0, 0), (-1, -1), "RIGHT"),
                ]),
            ),
        ]
    ]

    tabla_encabezado = Table(
        encabezado_factura,
        colWidths=[col_izq, col_der],
    )
    tabla_encabezado.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(tabla_encabezado)
    story.append(Spacer(1, 0.2 * inch))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_SECUNDARIO, spaceAfter=10))

    # ── Tabla de ítems ──
    encabezados = ["#", "Descripción", "Cant.", "Precio Unit.", "Desc. %", "Subtotal"]
    col_widths  = [0.35*inch, 3.0*inch, 0.55*inch, 1.1*inch, 0.7*inch, 1.3*inch]

    estilo_th = ParagraphStyle(
        "th", fontSize=8, textColor=colors.white,
        fontName="Helvetica-Bold", alignment=TA_CENTER
    )
    estilo_td_centro = ParagraphStyle(
        "td_c", fontSize=8, textColor=COLOR_TEXTO,
        fontName="Helvetica", alignment=TA_CENTER
    )
    estilo_td_izq = ParagraphStyle(
        "td_l", fontSize=8, textColor=COLOR_TEXTO,
        fontName="Helvetica", alignment=TA_LEFT
    )
    estilo_td_der = ParagraphStyle(
        "td_r", fontSize=8, textColor=COLOR_TEXTO,
        fontName="Helvetica", alignment=TA_RIGHT
    )

    filas = [[Paragraph(h, estilo_th) for h in encabezados]]

    subtotal_general = 0.0
    total_descuentos = 0.0

    for i, item in enumerate(items, start=1):
        desc     = item.get("descripcion", "")
        cantidad = float(item.get("cantidad", 1))
        precio   = float(item.get("precio_unit", 0))
        pct_desc = float(item.get("descuento", 0))

        valor_bruto    = cantidad * precio
        valor_desc     = valor_bruto * pct_desc / 100
        subtotal_item  = valor_bruto - valor_desc

        subtotal_general += subtotal_item
        total_descuentos += valor_desc

        filas.append([
            Paragraph(str(i), estilo_td_centro),
            Paragraph(desc,   estilo_td_izq),
            Paragraph(f"{cantidad:,.0f}", estilo_td_centro),
            Paragraph(f"${precio:,.0f}", estilo_td_der),
            Paragraph(f"{pct_desc:.0f}%", estilo_td_centro),
            Paragraph(f"${subtotal_item:,.0f}", estilo_td_der),
        ])

    tabla_items = Table(filas, colWidths=col_widths, repeatRows=1)

    # Estilo zebra
    item_style = [
        ("BACKGROUND",    (0, 0), (-1, 0), COLOR_PRIMARIO),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, COLOR_ACENTO]),
        ("GRID",          (0, 0), (-1, -1), 0.4, COLOR_LINEA),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]
    tabla_items.setStyle(TableStyle(item_style))
    story.append(tabla_items)
    story.append(Spacer(1, 0.15 * inch))

    # ── Totales ──
    iva_pct       = 0.19
    base_gravable = subtotal_general
    iva_valor     = base_gravable * iva_pct
    total_final   = base_gravable + iva_valor

    estilo_total_label = ParagraphStyle(
        "tl", fontSize=9, textColor=COLOR_TEXTO,
        fontName="Helvetica", alignment=TA_RIGHT
    )
    estilo_total_valor = ParagraphStyle(
        "tv", fontSize=9, textColor=COLOR_TEXTO,
        fontName="Helvetica-Bold", alignment=TA_RIGHT
    )
    estilo_gran_total_label = ParagraphStyle(
        "gtl", fontSize=11, textColor=colors.white,
        fontName="Helvetica-Bold", alignment=TA_RIGHT
    )
    estilo_gran_total_valor = ParagraphStyle(
        "gtv", fontSize=11, textColor=colors.white,
        fontName="Helvetica-Bold", alignment=TA_RIGHT
    )

    filas_totales = [
        [Paragraph("Subtotal:", estilo_total_label),
         Paragraph(f"${subtotal_general:,.0f}", estilo_total_valor)],
        [Paragraph(f"Descuentos:", estilo_total_label),
         Paragraph(f"-${total_descuentos:,.0f}", estilo_total_valor)],
        [Paragraph(f"IVA (19%):", estilo_total_label),
         Paragraph(f"${iva_valor:,.0f}", estilo_total_valor)],
        [Paragraph("TOTAL A PAGAR:", estilo_gran_total_label),
         Paragraph(f"${total_final:,.0f}", estilo_gran_total_valor)],
    ]

    tabla_totales = Table(
        filas_totales,
        colWidths=[5.8 * inch, 1.7 * inch],
        hAlign="RIGHT",
    )
    tabla_totales.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "RIGHT"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW",     (0, 2), (-1, 2), 0.5, COLOR_LINEA),
        ("BACKGROUND",    (0, 3), (-1, 3), COLOR_PRIMARIO),
        ("ROUNDEDCORNERS",(0, 3), (-1, 3), 4),
    ]))
    story.append(tabla_totales)

    # ── Notas ──
    if notas:
        story.append(Spacer(1, 0.25 * inch))
        story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_LINEA))
        story.append(Spacer(1, 6))
        story.append(Paragraph("Notas:", ParagraphStyle(
            "nota_titulo", fontSize=8, textColor=COLOR_PRIMARIO,
            fontName="Helvetica-Bold"
        )))
        story.append(Paragraph(notas, estilo_nota))

    # ── Build ──
    doc.build(
        story,
        canvasmaker=lambda *a, **kw: FacturaCanvas(*a, empresa=empresa, **kw),
    )
    return output_path