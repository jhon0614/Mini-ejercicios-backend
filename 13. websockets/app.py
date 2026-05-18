from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "cambia-esto-en-produccion")

socketio = SocketIO(app, logger=False, engineio_logger=False)

def timestamp():
    return datetime.now().strftime("%H:%M")

@app.route("/")
def home():
    return render_template("index.html")

@socketio.on("connect")
def on_connect():
    nick = request.args.get("nick", "Anónimo")[:20]
    print(f"[{timestamp()}] + {nick} conectado  (sid={request.sid})")
    emit(
        "sistema",
        {"mensaje": f"{nick} se unió al chat", "hora": timestamp()},
        broadcast=True,
    )

@socketio.on("disconnect")
def on_disconnect():
    nick = request.args.get("nick", "Anónimo")[:20]
    print(f"[{timestamp()}] - {nick} desconectado")
    emit(
        "sistema",
        {"mensaje": f"{nick} salió del chat", "hora": timestamp()},
        broadcast=True,
    )

@socketio.on("mensaje")
def on_mensaje(data):
    texto = data.get("mensaje", "").strip()
    nick  = data.get("nick", "Anónimo")[:20]

    if not texto:
        return
    if len(texto) > 500:
        emit("error", {"mensaje": "Mensaje demasiado largo (máx. 500 caracteres)"})
        return

    print(f"[{timestamp()}] {nick}: {texto}")

    emit(
        "respuesta",
        {
            "nick":    nick,
            "mensaje": texto,
            "hora":    timestamp(),
        },
        broadcast=True,
    )

if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)