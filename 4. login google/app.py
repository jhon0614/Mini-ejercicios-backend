from extensions import db, mail, oauth
from dotenv import load_dotenv
load_dotenv()

from config import Config
from flask import Flask, session

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail.init_app(app)
oauth.init_app(app)

google = oauth.register(
    name='google',
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

from routes.password import password_bp
from routes.auth import auth_bp

app.register_blueprint(password_bp)
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host="localhost")