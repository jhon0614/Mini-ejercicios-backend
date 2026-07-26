from datetime import datetime

from extensions import db


class QRCode(db.Model):
    __tablename__ = "qr_codes"

    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False, unique=True)
    fecha_creacion = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "contenido": self.contenido,
            "nombre_archivo": self.nombre_archivo,
            "fecha_creacion": self.fecha_creacion.isoformat()
        }