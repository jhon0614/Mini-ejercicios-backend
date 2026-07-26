from extensions import db
from models.autor import Autor
from models.categoria import Categoria
from models.libro import Libro


def crear_libro(data):
    titulo = data.get("titulo")
    isbn = data.get("isbn")
    anio_publicacion = data.get("anio_publicacion")
    autor_id = data.get("autor_id")
    categoria_id = data.get("categoria_id")

    if not titulo or not titulo.strip():
        return None, "El título es obligatorio"

    if not isbn or not isbn.strip():
        return None, "El ISBN es obligatorio"

    if not autor_id:
        return None, "El autor es obligatorio"

    if not categoria_id:
        return None, "La categoría es obligatoria"

    autor = db.session.get(Autor, autor_id)

    if not autor:
        return None, "El autor indicado no existe"

    categoria = db.session.get(
        Categoria,
        categoria_id
    )

    if not categoria:
        return None, "La categoría indicada no existe"

    libro_existente = Libro.query.filter_by(
        isbn=isbn.strip()
    ).first()

    if libro_existente:
        return None, "Ya existe un libro con ese ISBN"

    libro = Libro(
        titulo=titulo.strip(),
        isbn=isbn.strip(),
        anio_publicacion=anio_publicacion,
        autor_id=autor_id,
        categoria_id=categoria_id,
        disponible=data.get("disponible", True)
    )

    db.session.add(libro)
    db.session.commit()

    return libro, None


def listar_libros(filtros):
    consulta = Libro.query

    titulo = filtros.get("titulo")
    autor_id = filtros.get("autor_id")
    categoria_id = filtros.get("categoria_id")
    disponible = filtros.get("disponible")

    if titulo:
        consulta = consulta.filter(
            Libro.titulo.ilike(f"%{titulo}%")
        )

    if autor_id:
        consulta = consulta.filter(
            Libro.autor_id == autor_id
        )

    if categoria_id:
        consulta = consulta.filter(
            Libro.categoria_id == categoria_id
        )

    if disponible is not None:
        consulta = consulta.filter(
            Libro.disponible == disponible
        )

    return consulta.order_by(
        Libro.titulo.asc()
    ).all()


def obtener_libro(libro_id):
    return db.session.get(Libro, libro_id)


def actualizar_libro(libro, data):
    if "titulo" in data:
        titulo = data.get("titulo")

        if not titulo or not titulo.strip():
            return None, "El título no puede estar vacío"

        libro.titulo = titulo.strip()

    if "isbn" in data:
        isbn = data.get("isbn")

        if not isbn or not isbn.strip():
            return None, "El ISBN no puede estar vacío"

        isbn = isbn.strip()

        libro_existente = Libro.query.filter(
            Libro.isbn == isbn,
            Libro.id != libro.id
        ).first()

        if libro_existente:
            return None, "Ya existe otro libro con ese ISBN"

        libro.isbn = isbn

    if "anio_publicacion" in data:
        libro.anio_publicacion = data.get(
            "anio_publicacion"
        )

    if "disponible" in data:
        libro.disponible = bool(
            data.get("disponible")
        )

    if "autor_id" in data:
        autor_id = data.get("autor_id")
        autor = db.session.get(Autor, autor_id)

        if not autor:
            return None, "El autor indicado no existe"

        libro.autor_id = autor_id

    if "categoria_id" in data:
        categoria_id = data.get("categoria_id")

        categoria = db.session.get(
            Categoria,
            categoria_id
        )

        if not categoria:
            return None, (
                "La categoría indicada no existe"
            )

        libro.categoria_id = categoria_id

    db.session.commit()

    return libro, None


def eliminar_libro(libro):
    db.session.delete(libro)
    db.session.commit()