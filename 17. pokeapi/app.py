from flask import Flask, jsonify, render_template, request
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/pokemon")
def pokemon():

    nombre = request.args.get("nombre")

    if not nombre:
        return jsonify({
            "error": "Debe enviar nombre"
        }), 400

    url = f"https://pokeapi.co/api/v2/pokemon/{nombre.lower()}"

    response = requests.get(url)

    if response.status_code != 200:

        return jsonify({
            "error": "Pokemon no encontrado"
        }), 404

    data = response.json()

    pokemon = {
        "nombre": data["name"],
        "imagen": data["sprites"]["front_default"],
        "tipos": [
            t["type"]["name"]
            for t in data["types"]
        ],
        "habilidades": [
            h["ability"]["name"]
            for h in data["abilities"]
        ]
    }

    return jsonify(pokemon)

if __name__ == "__main__":
    app.run(debug=True)