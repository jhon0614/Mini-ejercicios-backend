from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from models import Usuario
from extensions import db
import bcrypt

auth_bp = Blueprint("auth", __name__)

# registro
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    existe = Usuario.query.filter_by(email=email).first()

    if existe:
        return jsonify({"error": "Usuario ya existe"}), 400

    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    usuario = Usuario(
        email=email,
        password=hashed.decode("utf-8")
    )

    db.session.add(usuario)
    db.session.commit()

    return jsonify({
        "message": "Usuario registrado"
    })

# login
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        return jsonify({"error": "Credenciales inválidas"}), 401

    valido = bcrypt.checkpw(
        password.encode("utf-8"),
        usuario.password.encode("utf-8")
    )

    if not valido:
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = create_access_token(
    identity=str(usuario.id),
    additional_claims={"rol": usuario.rol}
    )

    return jsonify({
        "token": token
    })

# ruta protegida
@auth_bp.route("/profile")
@jwt_required()
def profile():

    usuario_id = get_jwt_identity()

    return jsonify({
        "message": "Ruta protegida",
        "usuario_id": usuario_id
    })

@auth_bp.route("/admin")
@jwt_required()
def admin():

    claims = get_jwt()

    if claims["rol"] != "admin":
        return jsonify({
            "error": "Acceso denegado"
        }), 403

    return jsonify({
        "message": "Bienvenido admin"
    })