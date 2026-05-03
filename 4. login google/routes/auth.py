from flask import Blueprint, jsonify, session, redirect
from extensions import oauth, db
from models import Usuario


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login/google")
def login_google():
    google = oauth.create_client('google')
    return google.authorize_redirect(
        redirect_uri="http://localhost:5000/auth/google/callback"
    )

@auth_bp.route("/auth/google/callback")
def callback():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    user_info = token.get("userinfo")

    email = user_info["email"]
    provider_id = user_info["sub"] #id único google

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        usuario = Usuario(email=email, password="", provider_id=provider_id)
        db.session.add(usuario)
        db.session.commit()

    #sesión
    session["usuario_id"] = usuario.id
    session["email"] = usuario.email

    return redirect("/dashboard") #redirigir a la página principal

@auth_bp.route("/dashboard")
def dashboard():
    if "usuario_id" not in session:
        return redirect("/login")
    return jsonify({"message": f"Bienvenido {session['email']}"})

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")