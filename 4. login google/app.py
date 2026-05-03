from extensions import db, mail, oauth
from dotenv import load_dotenv
load_dotenv()
from config import Config
from flask import Flask

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail.init_app(app)
oauth.init_app(app)

from routes.password import password_bp
from routes.auth import auth_bp

app.register_blueprint(password_bp)
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)