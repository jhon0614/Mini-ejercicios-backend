from flask import Blueprint, jsonify, request

from services.categoria_service import (
    actualizar_categoria,
    crear_categoria,
    eliminar_categoria,
    listar_categorias,
    obtener_categoria
)

categoria_bp = Blueprint(
    "categorias",
    __name__,
    url_prefix="/api/categorias"
)


@categoria_bp.route("", methods=["POST"])
def registrar_categoria():
    data = request.get_json(silent=True) or {}

    categoria, error = crear_categoria(data)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "mensaje": "Categoría creada correctamente",
        "categoria": categoria.to_dict()
    }), 201


@categoria_bp.route("", methods=["GET"])
def consultar_categorias():
    categorias = listar_categorias()

    return jsonify([
        categoria.to_dict()
        for categoria in categorias
    ]), 200


@categoria_bp.route("/<int:categoria_id>", methods=["GET"])
def consultar_categoria(categoria_id):
    categoria = obtener_categoria(categoria_id)

    if not categoria:
        return jsonify({
            "error": "Categoría no encontrada"
        }), 404

    return jsonify(categoria.to_dict()), 200


@categoria_bp.route("/<int:categoria_id>", methods=["PUT"])
def editar_categoria(categoria_id):
    categoria = obtener_categoria(categoria_id)

    if not categoria:
        return jsonify({
            "error": "Categoría no encontrada"
        }), 404

    data = request.get_json(silent=True) or {}

    categoria, error = actualizar_categoria(
        categoria,
        data
    )

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "mensaje": "Categoría actualizada correctamente",
        "categoria": categoria.to_dict()
    }), 200


@categoria_bp.route(
    "/<int:categoria_id>",
    methods=["DELETE"]
)
def borrar_categoria(categoria_id):
    categoria = obtener_categoria(categoria_id)

    if not categoria:
        return jsonify({
            "error": "Categoría no encontrada"
        }), 404

    eliminada, error = eliminar_categoria(categoria)

    if not eliminada:
        return jsonify({"error": error}), 409

    return jsonify({
        "mensaje": "Categoría eliminada correctamente"
    }), 200