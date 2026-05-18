from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os, uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
MAX_FILE_SIZE_MB = 10

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE_MB * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "pdf"}

def archivo_permitido(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS
    )

@app.errorhandler(RequestEntityTooLarge)
def archivo_muy_grande(e):
    return jsonify({
        "error": f"El archivo supera el límite de {MAX_FILE_SIZE_MB} MB"
    }), 413

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "archivo" not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400

    archivo = request.files["archivo"]

    if archivo.filename == "":
        return jsonify({"error": "No se seleccionó ningún archivo"}), 400

    if not archivo_permitido(archivo.filename):
        return jsonify({
            "error": "Extensión no permitida. Solo se aceptan: PNG, JPG, JPEG, PDF"
        }), 400

    try:
        nombre_seguro = secure_filename(archivo.filename)
        nombre_unico = f"{uuid.uuid4()}_{nombre_seguro}"
        ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre_unico)
        archivo.save(ruta)
    except Exception as e:
        return jsonify({"error": "Error al guardar el archivo"}), 500

    return jsonify({
        "message": "Archivo subido correctamente",
        "archivo": nombre_unico
    }), 201

if __name__ == "__main__":
    app.run(debug=True)