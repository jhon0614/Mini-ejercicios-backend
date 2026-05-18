from flask import Flask, jsonify, render_template, request
import string, secrets

app = Flask(__name__)

MINUSCULAS = string.ascii_lowercase
MAYUSCULAS = string.ascii_uppercase
NUMEROS    = string.digits
ESPECIALES = "!@#$%^&*()"

def generar_password(longitud=12, usar_mayus=True, usar_nums=True, usar_esp=True):
    pool = MINUSCULAS
    obligatorios = [secrets.choice(MINUSCULAS)]

    if usar_mayus:
        pool += MAYUSCULAS
        obligatorios.append(secrets.choice(MAYUSCULAS))
    if usar_nums:
        pool += NUMEROS
        obligatorios.append(secrets.choice(NUMEROS))
    if usar_esp:
        pool += ESPECIALES
        obligatorios.append(secrets.choice(ESPECIALES))

    relleno = [secrets.choice(pool) for _ in range(longitud - len(obligatorios))]
    chars = obligatorios + relleno
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generar")
def generar():
    try:
        longitud = int(request.args.get("longitud", 12))
    except ValueError:
        return jsonify({"error": "Longitud inválida"}), 400

    if not (8 <= longitud <= 64):
        return jsonify({"error": "La longitud debe estar entre 8 y 64"}), 400

    def bool_param(name, default=True):
        v = request.args.get(name, str(default)).lower()
        return v not in ("false", "0", "no")

    usar_mayus = bool_param("mayusculas")
    usar_nums  = bool_param("numeros")
    usar_esp   = bool_param("especiales")

    password = generar_password(longitud, usar_mayus, usar_nums, usar_esp)
    return jsonify({"password": password, "longitud": len(password)})

if __name__ == "__main__":
    app.run(debug=True)