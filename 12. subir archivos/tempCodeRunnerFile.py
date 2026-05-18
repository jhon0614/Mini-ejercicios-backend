from flask import Flask, request, render_template, jsonify
import os, uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# crear carpeta si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EXTENSIONES_PERMITIDAS = {
    "png",
    "jpg",
    "jpeg",
    "pdf"
}

def archivo_permitido(filename):

    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower()
        in EXTENSIONES_PERMITIDAS
    )

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():

    if "archivo" not in request.files:
        return jsonify({
            "error": "No se envió archivo"
        }), 400

    archivo = request.files["archivo"]

    if archivo.filename == "":
        return jsonify({
            "error": "Archivo vacío"
        }), 400

    if not archivo_permitido(archivo.filename):
        return jsonify({
            "error": "Extensión no permitida"
        }), 400

    # generar nombre único
    nombre_unico = f"{uuid.uuid4()}_{archivo.filename}"

    # construir ruta
    ruta = os.path.join(
        app.config["UPLOAD_FOLDER"],
        nombre_unico
    )


    archivo.save(ruta)

    return jsonify({
        "message": "Archivo subido correctamente",
        "archivo": nombre_unico
    })

if __name__ == "__main__":
    app.run(debug=True)