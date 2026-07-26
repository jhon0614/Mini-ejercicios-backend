from extensions import db
from models.categoria import Categoria


def crear_categoria(data):
    nombre = data.get("nombre")

    if not nombre or not nombre.strip():
        return None, "El nombre de la categoría es obligatorio"

    nombre = nombre.strip()

    categoria_existente = Categoria.query.filter_by(
        nombre=nombre
    ).first()

    if categoria_existente:
        return None, "La categoría ya existe"

    categoria = Categoria(nombre=nombre)

    db.session.add(categoria)
    db.session.commit()

    return categoria, None


def listar_categorias():
    return Categoria.query.order_by(
        Categoria.nombre.asc()
    ).all()


def obtener_categoria(categoria_id):
    return db.session.get(Categoria, categoria_id)


def actualizar_categoria(categoria, data):
    nombre = data.get("nombre")

    if nombre is None or not nombre.strip():
        return None, "El nombre es obligatorio"

    nombre = nombre.strip()

    categoria_existente = Categoria.query.filter(
        Categoria.nombre == nombre,
        Categoria.id != categoria.id
    ).first()

    if categoria_existente:
        return None, "Ya existe otra categoría con ese nombre"

    categoria.nombre = nombre
    db.session.commit()

    return categoria, None


def eliminar_categoria(categoria):
    if categoria.libros:
        return False, (
            "No se puede eliminar la categoría "
            "porque tiene libros asociados"
        )

    db.session.delete(categoria)
    db.session.commit()

    return True, None