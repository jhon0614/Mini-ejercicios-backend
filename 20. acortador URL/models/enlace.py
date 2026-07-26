from datetime import datetime

from extensions import db


class Enlace(db.Model):
    __tablename__ = "enlaces"

    id = db.Column(db.Integer, primary_key=True)

    url_original = db.Column(
        db.Text,
        nullable=False
    )

    codigo_corto = db.Column(
        db.String(20),
        nullable=False,
        unique=True,
        index=True
    )

    visitas = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    fecha_creacion = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "url_original": self.url_original,
            "codigo_corto": self.codigo_corto,
            "visitas": self.visitas,
            "fecha_creacion": self.fecha_creacion.isoformat()
        }