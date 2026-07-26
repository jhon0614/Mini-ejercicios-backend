from flask import Flask, jsonify

from config import Config
from extensions import db
from models import Autor, Categoria, Libro
from routes import autor_bp, categoria_bp, libro_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(autor_bp)
    app.register_blueprint(categoria_bp)
    app.register_blueprint(libro_bp)

    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "mensaje": "API de Biblioteca funcionando",
            "endpoints": {
                "autores": "/api/autores",
                "categorias": "/api/categorias",
                "libros": "/api/libros"
            }
        })

    @app.errorhandler(404)
    def recurso_no_encontrado(error):
        return jsonify({
            "error": "Recurso no encontrado"
        }), 404

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)