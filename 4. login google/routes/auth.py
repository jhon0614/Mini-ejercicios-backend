from flask import Blueprint, jsonify
from extensions import oauth
from models import Usuario
from extensions import db
import os

auth_bp = Blueprint("auth", __name__)

google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@auth_bp.route("/login/google")
def login_google():
    return google.authorize_redirect(
        redirect_uri="http://localhost:5000/auth/google/callback"
    )

@auth_bp.route("/auth/google/callback")
def callback():
    token = google.authorize_access_token()
    user_info = google.parse_id_token(token)

    email = user_info["email"]

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        usuario = Usuario(email=email, password="")
        db.session.add(usuario)
        db.session.commit()

    return jsonify({"message": "Login con Google", "email": email})