from flask import Blueprint, jsonify, request

from services.autor_service import (
    actualizar_autor,
    crear_autor,
    eliminar_autor,
    listar_autores,
    obtener_autor
)

autor_bp = Blueprint(
    "autores",
    __name__,
    url_prefix="/api/autores"
)


@autor_bp.route("", methods=["POST"])
def registrar_autor():
    data = request.get_json(silent=True) or {}

    autor, error = crear_autor(data)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "mensaje": "Autor creado correctamente",
        "autor": autor.to_dict()
    }), 201


@autor_bp.route("", methods=["GET"])
def consultar_autores():
    autores = listar_autores()

    return jsonify([
        autor.to_dict()
        for autor in autores
    ]), 200


@autor_bp.route("/<int:autor_id>", methods=["GET"])
def consultar_autor(autor_id):
    autor = obtener_autor(autor_id)

    if not autor:
        return jsonify({
            "error": "Autor no encontrado"
        }), 404

    return jsonify(autor.to_dict()), 200


@autor_bp.route("/<int:autor_id>", methods=["PUT"])
def editar_autor(autor_id):
    autor = obtener_autor(autor_id)

    if not autor:
        return jsonify({
            "error": "Autor no encontrado"
        }), 404

    data = request.get_json(silent=True) or {}

    autor, error = actualizar_autor(autor, data)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "mensaje": "Autor actualizado correctamente",
        "autor": autor.to_dict()
    }), 200


@autor_bp.route("/<int:autor_id>", methods=["DELETE"])
def borrar_autor(autor_id):
    autor = obtener_autor(autor_id)

    if not autor:
        return jsonify({
            "error": "Autor no encontrado"
        }), 404

    eliminado, error = eliminar_autor(autor)

    if not eliminado:
        return jsonify({"error": error}), 409

    return jsonify({
        "mensaje": "Autor eliminado correctamente"
    }), 200