from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    url_for
)

from services.enlace_service import EnlaceService


enlace_bp = Blueprint("enlace", __name__)


@enlace_bp.route("/", methods=["GET"])
def inicio():
    enlaces = EnlaceService.listar_enlaces()

    return render_template(
        "index.html",
        enlaces=enlaces
    )


@enlace_bp.route("/api/enlaces", methods=["POST"])
def crear_enlace():
    data = request.get_json(silent=True) or request.form
    url_original = data.get("url_original")

    try:
        enlace = EnlaceService.crear_enlace(url_original)

        url_corta = url_for(
            "enlace.redirigir_enlace",
            codigo=enlace.codigo_corto,
            _external=True
        )

        return jsonify({
            "mensaje": "URL acortada correctamente",
            "enlace": enlace.to_dict(),
            "url_corta": url_corta
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except Exception as error:
        return jsonify({
            "error": "No fue posible acortar la URL",
            "detalle": str(error)
        }), 500


@enlace_bp.route("/api/enlaces", methods=["GET"])
def listar_enlaces():
    enlaces = EnlaceService.listar_enlaces()

    return jsonify([
        {
            **enlace.to_dict(),
            "url_corta": url_for(
                "enlace.redirigir_enlace",
                codigo=enlace.codigo_corto,
                _external=True
            )
        }
        for enlace in enlaces
    ])


@enlace_bp.route("/<codigo>", methods=["GET"])
def redirigir_enlace(codigo):
    enlace = EnlaceService.buscar_por_codigo(codigo)

    if not enlace:
        return jsonify({
            "error": "Enlace no encontrado"
        }), 404

    EnlaceService.registrar_visita(enlace)

    return redirect(enlace.url_original)


@enlace_bp.route(
    "/api/enlaces/<int:enlace_id>",
    methods=["DELETE"]
)
def eliminar_enlace(enlace_id):
    eliminado = EnlaceService.eliminar_enlace(enlace_id)

    if not eliminado:
        return jsonify({
            "error": "Enlace no encontrado"
        }), 404

    return jsonify({
        "mensaje": "Enlace eliminado correctamente"
    })