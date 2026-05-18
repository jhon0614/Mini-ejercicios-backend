from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)

REGLAS = [
    ("longitud",  lambda p: len(p) >= 8,                        "Mínimo 8 caracteres"),
    ("mayuscula", lambda p: bool(re.search(r"[A-Z]", p)),       "Al menos una mayúscula"),
    ("minuscula", lambda p: bool(re.search(r"[a-z]", p)),       "Al menos una minúscula"),
    ("numero",    lambda p: bool(re.search(r"\d", p)),           "Al menos un número"),
    ("especial",  lambda p: bool(re.search(r'[!@#$%^&*(),.?\":{}|<>]', p)), "Al menos un carácter especial (!@#…)"),
]

def calcular_fortaleza(password, errores):
    """0–100 basado en reglas cumplidas + longitud extra."""
    aprobadas = len(REGLAS) - len(errores)
    base = int(aprobadas / len(REGLAS) * 80)
    bonus = min(20, max(0, (len(password) - 8) * 2))
    return base + bonus

def validar_password(password):
    errores = []
    for _, fn, msg in REGLAS:
        if not fn(password):
            errores.append(msg)
    return errores

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/validar", methods=["POST"])
def validar():
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")

    if not isinstance(password, str):
        return jsonify({"valida": False, "errores": ["Formato inválido"]}), 400

    if len(password) > 128:
        return jsonify({"valida": False, "errores": ["La contraseña no puede superar 128 caracteres"]}), 400

    errores = validar_password(password)
    fortaleza = calcular_fortaleza(password, errores)

    if errores:
        return jsonify({"valida": False, "errores": errores, "fortaleza": fortaleza})

    return jsonify({"valida": True, "mensaje": "Contraseña segura", "fortaleza": fortaleza})

if __name__ == "__main__":
    app.run(debug=True)