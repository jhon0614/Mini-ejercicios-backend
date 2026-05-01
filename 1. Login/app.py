from flask import Flask, request, jsonify
from db import db
from models import Usuario
import bcrypt

app = Flask(__name__)

#conexión MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:admin@localhost/login_app"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# registro
@app.route('/registro', methods=['POST'])
def registro():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if Usuario.query.filter_by(email=email).first():
        return jsonify({'message': 'El email ya está registrado'}), 400
    
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()) #encriptar contraseña y realiza salto para no repetir mismo hash

    nuevo_usuario = Usuario(email=email, password=hashed.decode("utf-8"))
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({'message': 'Usuario registrado correctamente'}), 201

# login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        return jsonify({'message': 'Usuario no encontrado'}), 404
    
    if not bcrypt.checkpw(password.encode("utf-8"), usuario.password.encode("utf-8")):
        return jsonify({"error": "Contraseña incorrecta"}), 401

    return jsonify({"message": "Login exitoso"})


if __name__ == "__main__":
    app.run(debug=True)