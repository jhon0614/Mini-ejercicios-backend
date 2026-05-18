from flask import Flask
from config import Config
from extensions import db
from routes.producto_routes import producto_bp

app = Flask(__name__)

app.config.from_object(Config)
db.init_app(app)
app.register_blueprint(producto_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)