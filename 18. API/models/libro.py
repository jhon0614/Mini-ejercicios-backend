from extensions import db


class Libro(db.Model):
    __tablename__ = "libros"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(180), nullable=False)
    isbn = db.Column(
        db.String(20),
        nullable=False,
        unique=True
    )
    anio_publicacion = db.Column(db.Integer, nullable=True)
    disponible = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    autor_id = db.Column(
        db.Integer,
        db.ForeignKey("autores.id"),
        nullable=False
    )

    categoria_id = db.Column(
        db.Integer,
        db.ForeignKey("categorias.id"),
        nullable=False
    )

    autor = db.relationship(
        "Autor",
        back_populates="libros"
    )

    categoria = db.relationship(
        "Categoria",
        back_populates="libros"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "isbn": self.isbn,
            "anio_publicacion": self.anio_publicacion,
            "disponible": self.disponible,
            "autor": self.autor.to_dict(),
            "categoria": self.categoria.to_dict()
        }