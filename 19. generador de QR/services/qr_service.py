import os
import uuid

import qrcode

from extensions import db
from models.qr import QRCode


class QRService:

    @staticmethod
    def generar_qr(contenido, carpeta_destino):
        if not contenido or not contenido.strip():
            raise ValueError("El contenido es obligatorio")

        contenido = contenido.strip()

        nombre_archivo = f"{uuid.uuid4()}.png"
        ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)

        os.makedirs(carpeta_destino, exist_ok=True)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4
        )

        qr.add_data(contenido)
        qr.make(fit=True)

        imagen = qr.make_image(
            fill_color="black",
            back_color="white"
        )

        imagen.save(ruta_archivo)

        registro = QRCode(
            contenido=contenido,
            nombre_archivo=nombre_archivo
        )

        try:
            db.session.add(registro)
            db.session.commit()
            return registro
        except Exception:
            db.session.rollback()

            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)

            raise

    @staticmethod
    def listar_qr():
        return QRCode.query.order_by(
            QRCode.fecha_creacion.desc()
        ).all()

    @staticmethod
    def buscar_por_id(qr_id):
        return db.session.get(QRCode, qr_id)

    @staticmethod
    def eliminar_qr(qr_id, carpeta_destino):
        registro = db.session.get(QRCode, qr_id)

        if not registro:
            return False

        ruta_archivo = os.path.join(
            carpeta_destino,
            registro.nombre_archivo
        )

        try:
            db.session.delete(registro)
            db.session.commit()

            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)

            return True
        except Exception:
            db.session.rollback()
            raise