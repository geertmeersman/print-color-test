from flask import Flask, request, redirect, render_template, flash
from werkzeug.utils import secure_filename
import subprocess
import os

UPLOAD_FOLDER = "/tmp/uploads"
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default-secret")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or not file.filename.endswith(".pdf"):
        flash("Invalid file. Please upload a PDF.")
        return redirect("/")
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)
    try:
        subprocess.run(["/usr/bin/lp", "-d", "MyPrinter", filepath], check=True)
        flash("PDF sent to printer.")
    except subprocess.CalledProcessError:
        flash("Failed to print PDF.")
    return redirect("/")

@app.route("/print-test", methods=["POST"])
def print_test():
    try:
        subprocess.run(["/home/test_empty.sh"], check=True)
        flash("Test job sent.")
    except subprocess.CalledProcessError:
        flash("Failed to send test job.")
    return redirect("/")

@app.route("/status")
def status():
    try:
        out = subprocess.check_output(["/usr/bin/lpstat", "-p", "MyPrinter"], text=True)
    except subprocess.CalledProcessError:
        out = "Could not fetch printer status."
    return f"<pre>{out}</pre>"
