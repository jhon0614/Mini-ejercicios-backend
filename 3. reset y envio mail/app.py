from flask import Flask, request, jsonify, render_template
from flask_mail import Mail, Message
from db import db
from models import Usuario, PasswordToken
from datetime import datetime, timedelta, timezone
import bcrypt
import uuid

#conexión a la bd
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost:3306/reset_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#configuración mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jhonri.0614@gmail.com'
app.config['MAIL_PASSWORD'] = 'iqsl rwqd foks ziqo' #contraseña de aplicación gmail
mail = Mail(app)

db.init_app(app)
with app.app_context():
    db.create_all()

# solicitar reset password
@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get('email')    
    
    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    
    token = str(uuid.uuid4())
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=15)

    nuevo_token = PasswordToken(
        usuario_id = usuario.id,
        token = token,
        expiracion = expiracion
    )

    db.session.add(nuevo_token)
    db.session.commit()

    msg = Message(
        subject="Restablecer contraseña",
        sender=app.config['MAIL_USERNAME'],
        recipients=[email]
    )

    msg.html = f"""
        <h2>Restablecer contraseña</h2>
        <p>Haz clic en el siguiente botón:</p>
        <a href="http://127.0.0.1:5000/reset.html?token={token}">
            Resetear contraseña
        </a>
        <p>Expira en 15 minutos.</p>
        """

    try:
        mail.send(msg)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'message': 'Correo de restablecimiento enviado'}), 200

# direccionamiento página
@app.route("/reset.html")
def reset_page():
    return render_template('reset.html')

#resetear contraseña
@app.route("/reset-password", methods=["GET","POST"])
def reset_password():
    data = request.get_json()
    token = data.get('token')
    nueva_password = data.get('clave')

    registro = PasswordToken.query.filter_by(token=token).first()

    if not registro:
        return jsonify({'error': 'Token no valido o expirado'}), 400
    
    if not nueva_password:
        return jsonify({'error': 'Debe enviar nueva_password'}), 400

    if registro.usado:
        return jsonify({'error': 'Token ya usado'}), 400

    if registro.expiracion < datetime.utcnow():
        return jsonify({'error': 'Token no valido o expirado'}), 400
    
    usuario = Usuario.query.get(registro.usuario_id)
    hashed = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt())
    usuario.password = hashed.decode('utf-8')

    registro.usado = True
    db.session.commit()

    return jsonify({'message': 'Contraseña actualizada correctamente'}), 200

if __name__ == "__main__":
    app.run(debug=True)