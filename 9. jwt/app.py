
from dotenv import load_dotenv
load_dotenv()
from extensions import db, jwt
from routes.auth import auth_bp



from flask import Flask
from config import Config
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt.init_app(app)

app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)