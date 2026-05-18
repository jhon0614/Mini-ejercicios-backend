from models.producto import Producto
from extensions import db

def crear_producto(data):

    producto = Producto(
        nombre=data["nombre"],
        precio=data["precio"]
    )

    db.session.add(producto)
    db.session.commit()

    return producto

def obtener_productos():
    return Producto.query.all()

def obtener_producto(id):
    return Producto.query.get(id)

def actualizar_producto(producto, data):
    producto.nombre = data["nombre"]
    producto.precio = data["precio"]
    db.session.commit()
    return producto

def eliminar_producto(producto):
    db.session.delete(producto)
    db.session.commit()