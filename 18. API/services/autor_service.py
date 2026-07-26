from extensions import db
from models.autor import Autor

def crear_autor(data):
    nombre = data.get("nombre")
    nacionalidad = data.get("nacionalidad")

    if not nombre or not nombre.strip():
        return None, "El nombre del autor es obligatorio"

    autor = Autor(
        nombre=nombre.strip(),
        nacionalidad=nacionalidad.strip()
        if isinstance(nacionalidad, str)
        else nacionalidad
    )

    db.session.add(autor)
    db.session.commit()

    return autor, None


def listar_autores():
    return Autor.query.order_by(Autor.nombre.asc()).all()


def obtener_autor(autor_id):
    return db.session.get(Autor, autor_id)


def actualizar_autor(autor, data):
    nombre = data.get("nombre")
    nacionalidad = data.get("nacionalidad")

    if nombre is not None:
        if not nombre.strip():
            return None, "El nombre no puede estar vacío"

        autor.nombre = nombre.strip()

    if nacionalidad is not None:
        autor.nacionalidad = nacionalidad.strip()

    db.session.commit()

    return autor, None


def eliminar_autor(autor):
    if autor.libros:
        return False, (
            "No se puede eliminar el autor porque tiene libros asociados"
        )

    db.session.delete(autor)
    db.session.commit()

    return True, None