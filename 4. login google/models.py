from db import db
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    provider = db.Column(db.String(50))
    provider_id = db.Column(db.String(255))

class PasswordToken(db.Model):
    __tablename__ = 'password_tokens'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer)
    token = db.Column(db.String(255))
    expiracion = db.Column(db.DateTime(timezone=True))
    usado = db.Column(db.Boolean, default=False)