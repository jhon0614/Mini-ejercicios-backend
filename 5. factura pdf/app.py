"""
app.py  —  Ejemplo Flask que genera y devuelve una factura PDF profesional.
"""

import os
import tempfile
from flask import Flask, send_file, request, jsonify
from pdf_generator import generar_factura_pdf

app = Flask(__name__)


# ──────────────────────────────────────────────────────────────
#  Datos de tu empresa (muévelos a config/env en producción)
# ──────────────────────────────────────────────────────────────
EMPRESA = {
    "nombre":    "PaperControl.",
    "nit":       "NIT: 900.123.456-7",
    "direccion": "Calle 50 #40-20, Medellín, Antioquia",
    "telefono":  "Tel: +57 604 555 0000",
    "email":     "facturacion@papercontrol.com",
    "pie":       "www.papercontrol.com  |  facturacion@papercontrol.com  |  +57 604 555 0000",
}


# ──────────────────────────────────────────────────────────────
#  GET /factura  →  factura de ejemplo hardcodeada
# ──────────────────────────────────────────────────────────────
@app.route("/factura")
def factura_ejemplo():
    cliente = {
        "nombre":    "Jhon Pérez",
        "nit":       "1.000.123.456",
        "direccion": "Carrera 45 #22-10, Medellín",
        "email":     "jhon@gmail.com",
    }

    items = [
        {"descripcion": "Desarrollo módulo de ventas",  "cantidad": 1,  "precio_unit": 2_500_000, "descuento": 0},
        {"descripcion": "Soporte técnico mensual",      "cantidad": 3,  "precio_unit":   350_000, "descuento": 10},
        {"descripcion": "Licencia software anual",      "cantidad": 1,  "precio_unit": 1_200_000, "descuento": 5},
        {"descripcion": "Capacitación (hora)",          "cantidad": 8,  "precio_unit":   120_000, "descuento": 0},
    ]

    notas = (
        "Pago dentro de 30 días calendario. Transferencia bancaria: "
        "Bancolombia cta. 123-456789-00. "
        "Esta factura es un documento válido conforme a la normativa DIAN."
    )

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.close()

    generar_factura_pdf(
        output_path=tmp.name,
        numero_factura="FAC-2025-0042",
        fecha=None,          # usa fecha actual automáticamente
        cliente=cliente,
        items=items,
        empresa=EMPRESA,
        notas=notas,
    )

    return send_file(
        tmp.name,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="FAC-2025-0042.pdf",
    )


# ──────────────────────────────────────────────────────────────
#  POST /factura  →  genera factura con datos enviados en JSON
#
#  Body esperado:
#  {
#    "numero_factura": "FAC-2025-0043",
#    "fecha": "15/05/2025",          // opcional
#    "cliente": { "nombre": ..., "nit": ..., "direccion": ..., "email": ... },
#    "items": [
#      { "descripcion": ..., "cantidad": ..., "precio_unit": ..., "descuento": ... }
#    ],
#    "notas": "..."                  // opcional
#  }
# ──────────────────────────────────────────────────────────────
@app.route("/factura", methods=["POST"])
def factura_desde_json():
    data = request.get_json(force=True)

    numero   = data.get("numero_factura", "FAC-SIN-NUMERO")
    fecha    = data.get("fecha")
    cliente  = data.get("cliente", {})
    items    = data.get("items", [])
    notas    = data.get("notas", "")

    if not items:
        return jsonify({"error": "Se requiere al menos un ítem en la factura."}), 400

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.close()

    generar_factura_pdf(
        output_path=tmp.name,
        numero_factura=numero,
        fecha=fecha,
        cliente=cliente,
        items=items,
        empresa=EMPRESA,
        notas=notas,
    )

    return send_file(
        tmp.name,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{numero}.pdf",
    )


if __name__ == "__main__":
    app.run(debug=True)