import os
import sys
import json
from flask import jsonify
from flask import Flask, render_template, request, redirect, session
from PyPDF2 import PdfReader
from deep_translator import GoogleTranslator

from nlp_module.preprocessing import preprocess_text
from nlp_module.simplification import simplify_legal_text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

app = Flask(__name__)
app.secret_key = "secret_key_for_login"

users = {}

# ---------------- FILE READER ----------------
def read_uploaded_file(file):
    name = file.filename.lower()
    if name.endswith(".txt"):
        return file.read().decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
        return text
    return ""

# ---------------- LOGIN ----------------
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("username")
    password = request.form.get("password")

    if email in users and users[email] == password:
        session["user"] = email
        return redirect("/dashboard")

    return render_template("login.html", error="Invalid login")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("username")
        password = request.form.get("password")
        users[email] = password
        return redirect("/")
    return render_template("register.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")

# ---------------- PROCESS DOCUMENT ----------------
@app.route("/process", methods=["POST"])
def process():
    if "user" not in session:
        return redirect("/")

    text = ""
    if "document" in request.files and request.files["document"].filename:
        text = read_uploaded_file(request.files["document"])
    else:
        text = request.form.get("text", "")

    if not text.strip():
        return render_template("result.html", summary="No text provided")

    cleaned = preprocess_text(text)
    simplified = simplify_legal_text(cleaned)

    return render_template(
        "result.html",
        summary=simplified
    )

# ---------------- TRANSLATE SUMMARY ----------------
@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    text = data.get("text", "")
    lang = data.get("lang", "en")

    if lang == "en":
        return {"translated": text}

    try:
        translated = GoogleTranslator(source="en", target=lang).translate(text)
    except Exception:
        translated = text

    return {"translated": translated}

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/legal-help", methods=["POST"])
def legal_help():
    data = request.get_json()
    word = data.get("word", "").strip().lower()

    if not word:
        return jsonify({"meaning": "Please enter a legal term."})

    # Load legal dictionary
    json_path = os.path.join(os.path.dirname(__file__), "legal_dictionary.json")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            legal_dict = json.load(f)
    except Exception:
        return jsonify({"meaning": "Legal dictionary not found."})

    # Lookup word
    meaning = legal_dict.get(word)

    if meaning:
        return jsonify({"meaning": meaning})
    else:
        return jsonify({"meaning": "No definition found for this legal term."})

if __name__ == "__main__":
    app.run(debug=True)
