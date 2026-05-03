from flask import Blueprint, request, jsonify, render_template
from extensions import db, mail
from models import Usuario, PasswordToken
from flask_mail import Message
from datetime import datetime, timedelta
import uuid, bcrypt

password_bp = Blueprint("password", __name__)

@password_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get('email')    
    
    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    
    token = str(uuid.uuid4())
    expiracion = datetime.utcnow() + timedelta(minutes=15)

    nuevo_token = PasswordToken(
        usuario_id=usuario.id,
        token=token,
        expiracion=expiracion
    )

    db.session.add(nuevo_token)
    db.session.commit()

    msg = Message(
        subject="Restablecer contraseña",
        recipients=[email]
    )

    msg.html = f"""
    <h2>Restablecer contraseña</h2>
    <a href="http://127.0.0.1:5000/reset.html?token={token}">
        Resetear contraseña
    </a>
    """

    mail.send(msg)

    return jsonify({'message': 'Correo enviado'}), 200