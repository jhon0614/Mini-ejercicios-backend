"""
app.py  —  Flask con interfaz web para generar y enviar facturas PDF.
"""

import os
import tempfile
from flask import Flask, render_template, send_file, request, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv
from pdf_generator import generar_factura_pdf

load_dotenv()

app = Flask(__name__)

# ── Configuración de correo (lee desde .env) ──────────────────
app.config["MAIL_SERVER"]   = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"]     = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"]  = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)

EMPRESA = {
    "nombre":    os.getenv("EMPRESA_NOMBRE",    "Mi Empresa S.A.S."),
    "nit":       os.getenv("EMPRESA_NIT",       "NIT: 900.123.456-7"),
    "direccion": os.getenv("EMPRESA_DIRECCION", "Calle 50 #40-20, Medellín, Antioquia"),
    "telefono":  os.getenv("EMPRESA_TELEFONO",  "Tel: +57 604 555 0000"),
    "email":     os.getenv("EMPRESA_EMAIL",     "facturacion@miempresa.com"),
    "pie":       os.getenv("EMPRESA_PIE",       "www.miempresa.com  |  facturacion@miempresa.com"),
}


# ── Helpers ───────────────────────────────────────────────────
def _construir_factura(data: dict) -> tuple[str, str]:
    """Genera el PDF en un archivo temporal. Devuelve (ruta_tmp, numero)."""
    numero  = data.get("numero_factura", "FAC-SIN-NUMERO")
    fecha   = data.get("fecha")
    cliente = data.get("cliente", {})
    items   = data.get("items", [])
    notas   = data.get("notas", "")

    if not items:
        raise ValueError("Se requiere al menos un ítem en la factura.")

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
    return tmp.name, numero


# ── Página principal ──────────────────────────────────────────
@app.route("/")
def index():
    return render_template("factura_form.html")


# ── POST /factura → descarga el PDF ──────────────────────────
@app.route("/factura", methods=["POST"])
def factura_desde_json():
    data = request.get_json(force=True)
    try:
        ruta, numero = _construir_factura(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return send_file(
        ruta,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{numero}.pdf",
    )


# ── POST /enviar-factura → genera PDF y lo envía por correo ──
@app.route("/enviar-factura", methods=["POST"])
def enviar_factura():
    data = request.get_json(force=True)

    try:
        ruta, numero = _construir_factura(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Destinatario: email del cliente o uno explícito en el payload
    email_destino = (
        data.get("email_destino")
        or data.get("cliente", {}).get("email")
    )
    if not email_destino:
        return jsonify({"error": "No se encontró un correo destino para el cliente."}), 400

    nombre_cliente = data.get("cliente", {}).get("nombre", "Cliente")

    try:
        with open(ruta, "rb") as f:
            pdf_bytes = f.read()

        msg = Message(
            subject=f"Factura {numero} — {EMPRESA['nombre']}",
            sender=os.getenv("MAIL_USERNAME"),
            recipients=[email_destino],
        )
        msg.body = (
            f"Hola {nombre_cliente},\n\n"
            f"Adjunto encontrarás la factura {numero} emitida por {EMPRESA['nombre']}.\n\n"
            f"Ante cualquier duda, contáctanos a {EMPRESA['email']}.\n\n"
            "Gracias por tu preferencia."
        )
        msg.attach(
            filename=f"{numero}.pdf",
            content_type="application/pdf",
            data=pdf_bytes,
        )

        mail.send(msg)

    except Exception as e:
        return jsonify({"error": f"Error al enviar el correo: {str(e)}"}), 500
    finally:
        os.unlink(ruta)   # limpia el temporal siempre

    return jsonify({"ok": True, "mensaje": f"Factura enviada a {email_destino}."})


if __name__ == "__main__":
    app.run(debug=True, host="localhost")