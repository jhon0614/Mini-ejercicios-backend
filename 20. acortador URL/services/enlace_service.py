import secrets
import string
from urllib.parse import urlparse

from extensions import db
from models.enlace import Enlace


class EnlaceService:

    CARACTERES = string.ascii_letters + string.digits

    @staticmethod
    def validar_url(url):
        if not url or not url.strip():
            raise ValueError("La URL es obligatoria")

        url = url.strip()

        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        resultado = urlparse(url)

        if not resultado.netloc:
            raise ValueError("La URL no es válida")

        return url

    @classmethod
    def generar_codigo(cls, longitud=7):
        while True:
            codigo = "".join(
                secrets.choice(cls.CARACTERES)
                for _ in range(longitud)
            )

            existe = Enlace.query.filter_by(
                codigo_corto=codigo
            ).first()

            if not existe:
                return codigo

    @classmethod
    def crear_enlace(cls, url_original):
        url_original = cls.validar_url(url_original)
        codigo = cls.generar_codigo()

        enlace = Enlace(
            url_original=url_original,
            codigo_corto=codigo
        )

        try:
            db.session.add(enlace)
            db.session.commit()
            return enlace
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def listar_enlaces():
        return Enlace.query.order_by(
            Enlace.fecha_creacion.desc()
        ).all()

    @staticmethod
    def buscar_por_codigo(codigo):
        return Enlace.query.filter_by(
            codigo_corto=codigo
        ).first()

    @staticmethod
    def registrar_visita(enlace):
        enlace.visitas += 1

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def eliminar_enlace(enlace_id):
        enlace = db.session.get(Enlace, enlace_id)

        if not enlace:
            return False

        try:
            db.session.delete(enlace)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise