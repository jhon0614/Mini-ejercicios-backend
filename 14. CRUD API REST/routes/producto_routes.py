from flask import Blueprint, request, jsonify

from services.producto_service import (
    crear_producto,
    obtener_productos,
    obtener_producto,
    actualizar_producto,
    eliminar_producto
)

producto_bp = Blueprint(
    "productos",
    __name__
)

# crear
@producto_bp.route("/productos", methods=["POST"])
def create():
    data = request.get_json()
    producto = crear_producto(data)
    return jsonify(producto.to_dict())

# listar
@producto_bp.route("/productos", methods=["GET"])
def get_all():
    productos = obtener_productos()
    return jsonify([
        p.to_dict()
        for p in productos
    ])

# obtener uno
@producto_bp.route("/productos/<int:id>", methods=["GET"])
def get_one(id):
    producto = obtener_producto(id)
    if not producto:
        return jsonify({
            "error": "Producto no encontrado"
        }), 404
    return jsonify(producto.to_dict())

# actualizar
@producto_bp.route("/productos/<int:id>", methods=["PUT"])
def update(id):
    producto = obtener_producto(id)
    if not producto:
        return jsonify({
            "error": "Producto no encontrado"
        }), 404
    data = request.get_json()
    producto = actualizar_producto(
        producto,
        data
    )
    return jsonify(producto.to_dict())

# eliminar
@producto_bp.route("/productos/<int:id>", methods=["DELETE"])
def delete(id):
    producto = obtener_producto(id)
    if not producto:
        return jsonify({
            "error": "Producto no encontrado"
        }), 404
    eliminar_producto(producto)
    return jsonify({
        "message": "Producto eliminado"
    })