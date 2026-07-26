from extensions import db


class Autor(db.Model):
    __tablename__ = "autores"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    nacionalidad = db.Column(db.String(80), nullable=True)

    libros = db.relationship(
        "Libro",
        back_populates="autor",
        lazy=True
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "nacionalidad": self.nacionalidad
        }