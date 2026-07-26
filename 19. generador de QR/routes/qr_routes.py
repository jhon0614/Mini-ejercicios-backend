import os

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template,
    request,
    send_from_directory
)

from services.qr_service import QRService


qr_bp = Blueprint("qr", __name__)


def obtener_carpeta_qr():
    return os.path.join(
        current_app.root_path,
        "static",
        "qr"
    )


@qr_bp.route("/", methods=["GET"])
def inicio():
    registros = QRService.listar_qr()
    return render_template("index.html", registros=registros)


@qr_bp.route("/api/qr", methods=["POST"])
def generar_qr():
    data = request.get_json(silent=True) or request.form
    contenido = data.get("contenido")

    try:
        registro = QRService.generar_qr(
            contenido,
            obtener_carpeta_qr()
        )

        return jsonify({
            "mensaje": "Código QR generado correctamente",
            "qr": registro.to_dict(),
            "imagen_url": f"/qr/{registro.nombre_archivo}",
            "descarga_url": f"/qr/{registro.nombre_archivo}/descargar"
        }), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception as error:
        return jsonify({
            "error": "No fue posible generar el código QR",
            "detalle": str(error)
        }), 500


@qr_bp.route("/api/qr", methods=["GET"])
def listar_qr():
    registros = QRService.listar_qr()

    return jsonify([
        {
            **registro.to_dict(),
            "imagen_url": f"/qr/{registro.nombre_archivo}",
            "descarga_url": f"/qr/{registro.nombre_archivo}/descargar"
        }
        for registro in registros
    ])


@qr_bp.route("/qr/<nombre_archivo>", methods=["GET"])
def ver_qr(nombre_archivo):
    return send_from_directory(
        obtener_carpeta_qr(),
        nombre_archivo
    )


@qr_bp.route("/qr/<nombre_archivo>/descargar", methods=["GET"])
def descargar_qr(nombre_archivo):
    return send_from_directory(
        obtener_carpeta_qr(),
        nombre_archivo,
        as_attachment=True
    )


@qr_bp.route("/api/qr/<int:qr_id>", methods=["DELETE"])
def eliminar_qr(qr_id):
    eliminado = QRService.eliminar_qr(
        qr_id,
        obtener_carpeta_qr()
    )

    if not eliminado:
        return jsonify({
            "error": "Código QR no encontrado"
        }), 404

    return jsonify({
        "mensaje": "Código QR eliminado correctamente"
    })