"""
app.py  —  Flask con interfaz web para generar facturas PDF.
"""

import os
import tempfile
from flask import Flask, render_template, send_file, request, jsonify
from pdf_generator import generar_factura_pdf

app = Flask(__name__)

EMPRESA = {
    "nombre":    "Mi Empresa S.A.S.",
    "nit":       "NIT: 900.123.456-7",
    "direccion": "Calle 50 #40-20, Medellín, Antioquia",
    "telefono":  "Tel: +57 604 555 0000",
    "email":     "facturacion@miempresa.com",
    "pie":       "www.miempresa.com  |  facturacion@miempresa.com  |  +57 604 555 0000",
}


# ── Página principal: formulario web ──────────────────────────
@app.route("/")
def index():
    return render_template("factura_form.html")


# ── POST /factura: recibe JSON, devuelve PDF ───────────────────
@app.route("/factura", methods=["POST"])
def factura_desde_json():
    data = request.get_json(force=True)

    numero  = data.get("numero_factura", "FAC-SIN-NUMERO")
    fecha   = data.get("fecha")
    cliente = data.get("cliente", {})
    items   = data.get("items", [])
    notas   = data.get("notas", "")

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
    app.run(debug=True, host="localhost")