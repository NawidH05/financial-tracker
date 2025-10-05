# app.py
# ---------------------------------------------
# Flask Personal Finance Tracker
# Connects to MongoDB Atlas, stores transactions,
# and displays them in a dashboard with charts.
# ---------------------------------------------

from flask import Flask, render_template, request, redirect, url_for
from collections import defaultdict
from pymongo import MongoClient # type: ignore
from bson.objectid import ObjectId # type: ignore
from dotenv import load_dotenv  # type: ignore
import os

# ---------------------------------------------
# Load environment variables from .env
# ---------------------------------------------
load_dotenv()  
mongo_uri = os.getenv("MONGO_URI")  # Get connection string from .env

# ---------------------------------------------
# Connect to MongoDB Atlas
# ---------------------------------------------
client = MongoClient(mongo_uri)
db = client["finance_app"]  # Database name
transactions_collection = db["transactions"]  # Collection name

# ---------------------------------------------
# Flask app setup
# ---------------------------------------------
app = Flask(__name__)

# ---------------------------------------------
# Route: Summary Dashboard
# ---------------------------------------------
@app.route("/summary")
def summary():
    transactions = list(transactions_collection.find())

    # Convert ObjectId to string for Jinja templates
    for t in transactions:
        t["_id"] = str(t["_id"])

    # Calculate totals
    total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
    total_expenses = sum(t["amount"] for t in transactions if t["type"] == "expense")
    balance = total_income - total_expenses

    # Group by category
    category_totals = {}
    for t in transactions:
        category_totals[t["category"]] = category_totals.get(t["category"], 0) + t["amount"]

    return render_template(
        "summary.html",
        income=total_income,
        expenses=total_expenses,
        balance=balance,
        transactions=transactions,
        category_totals=category_totals
    )

# ---------------------------------------------
# Route: Add Transaction (POST)
# ---------------------------------------------
@app.route("/add", methods=["POST"])
def add_transaction():
    t_type = request.form["type"]
    amount = float(request.form["amount"])
    category = request.form["category"]

    transactions_collection.insert_one({
        "type": t_type,
        "amount": amount,
        "category": category
    })

    return redirect(url_for("summary"))

# ---------------------------------------------
# Route: Delete Transaction
# ---------------------------------------------
@app.route("/delete/<id>")
def delete_transaction(id):
    transactions_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("summary"))

# ---------------------------------------------
# Route: Home (Add Transaction Page)
# ---------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------------------------------------
# Run Flask app
# ---------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
