from extensions import db

class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(
        db.String(80),
        nullable=False,
        unique=True
    )

    libros = db.relationship(
        "Libro",
        back_populates="categoria",
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre
        }