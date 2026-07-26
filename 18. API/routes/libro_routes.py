from flask import Blueprint, jsonify, request

from services.libro_service import (
    actualizar_libro,
    crear_libro,
    eliminar_libro,
    listar_libros,
    obtener_libro
)

libro_bp = Blueprint(
    "libros",
    __name__,
    url_prefix="/api/libros"
)


@libro_bp.route("", methods=["POST"])
def registrar_libro():
    data = request.get_json(silent=True) or {}

    libro, error = crear_libro(data)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "mensaje": "Libro creado correctamente",
        "libro": libro.to_dict()
    }), 201


@libro_bp.route("", methods=["GET"])
def consultar_libros():
    disponible_param = request.args.get("disponible")

    disponible = None

    if disponible_param is not None:
        if disponible_param.lower() == "true":
            disponible = True
        elif disponible_param.lower() == "false":
            disponible = False
        else:
            return jsonify({
                "error": (
                    "El filtro disponible debe ser "
                    "true o false"
                )
            }), 400

    filtros = {
        "titulo": request.args.get("titulo"),
        "autor_id": request.args.get(
            "autor_id",
            type=int
        ),
        "categoria_id": request.args.get(
            "categoria_id",
            type=int
        ),
        "disponible": disponible
    }

    libros = listar_libros(filtros)

    return jsonify([
        libro.to_dict()
        for libro in libros
    ]), 200


@libro_bp.route("/<int:libro_id>", methods=["GET"])
def consultar_libro(libro_id):
    libro = obtener_libro(libro_id)

    if not libro:
        return jsonify({
            "error": "Libro no encontrado"
        }), 404

    return jsonify(libro.to_dict()), 200


@libro_bp.route("/<int:libro_id>", methods=["PUT"])
def editar_libro(libro_id):
    libro = obtener_libro(libro_id)

    if not libro:
        return jsonify({
            "error": "Libro no encontrado"
        }), 404

    data = request.get_json(silent=True) or {}

    libro, error = actualizar_libro(libro, data)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "mensaje": "Libro actualizado correctamente",
        "libro": libro.to_dict()
    }), 200


@libro_bp.route("/<int:libro_id>", methods=["DELETE"])
def borrar_libro(libro_id):
    libro = obtener_libro(libro_id)

    if not libro:
        return jsonify({
            "error": "Libro no encontrado"
        }), 404

    eliminar_libro(libro)

    return jsonify({
        "mensaje": "Libro eliminado correctamente"
    }), 200