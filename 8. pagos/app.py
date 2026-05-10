from flask import Flask, render_template, redirect, request
from dotenv import load_dotenv
from config import Config
import stripe

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

stripe.api_key = app.config["STRIPE_SECRET_KEY"]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Curso Python"
                    },
                    "unit_amount": 1000
                },
                "quantity": 1
            }
        ],
        mode="payment",
        success_url="http://localhost:5000/success",
        cancel_url="http://localhost:5000/cancel"
    )

    return redirect(session.url)

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/cancel")
def cancel():
    return render_template("cancel.html")

if __name__ == "__main__":
    app.run(debug=True)