import os
import uuid
import json
import subprocess
import sys
from functools import wraps
from flask import (
    Flask, render_template, request, send_from_directory,
    jsonify, redirect, url_for, Response, session
)
from werkzeug.utils import secure_filename
from fuzzy_logic import calculate_fuzzy_score
from uploads.ann_predictor import predict_ann_score_from_resume

app = Flask(__name__)
app.secret_key = "change_this_to_a_random_secret_key"

# ================================
# 🔐 REQUIRED FOR HUGGING FACE
# ================================
# Hugging Face runs Spaces in an iframe.
# Without these, browser drops cookies → login redirect loop.
if os.getenv("SPACE_ID"):  # Only on Hugging Face
    app.config["SESSION_COOKIE_SAMESITE"] = "None"
    app.config["SESSION_COOKIE_SECURE"] = True

# ================================
# Paths & Constants
# ================================
UPLOAD_FOLDER = 'uploads'
SCORES_FILE = 'scores.json'
FUZZY_FILE = 'fuzzy_scores.json'
ANN_FILE = 'ann_scores.json'
JD_FILE = 'job_description.txt'

HR_PASSCODE = "hr"
ADMIN_PASSCODE = "admin"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================================
# Helpers
# ================================
def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def load_jd():
    if os.path.exists(JD_FILE):
        with open(JD_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_jd(content):
    with open(JD_FILE, "w", encoding="utf-8") as f:
        f.write(content)

scores = load_json(SCORES_FILE)
fuzzy_scores = load_json(FUZZY_FILE)
ann_scores = load_json(ANN_FILE)

# ================================
# Security Decorators
# ================================
def hr_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("hr_logged_in"):
            return redirect(url_for("hr_login"))
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapper

# ================================
# Pages
# ================================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/user")
def user_page():
    return render_template("user.html")

# ================================
# HR Dashboard (Protected)
# ================================
@app.route("/hr", methods=["GET"])
@hr_required
def hr_dashboard():
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if os.path.isfile(os.path.join(UPLOAD_FOLDER, filename)):
            file_id = filename.split(".")[0]
            files.append({
                "id": file_id,
                "filename": filename,
                "score": scores.get(file_id, "Not yet scored"),
                "suggested_score": fuzzy_scores.get(file_id, "0"),
                "ann_score": ann_scores.get(file_id, "0")
            })

    return render_template(
        "hr.html",
        files=files,
        jd_content=load_jd()
    )

# ================================
# Update JD + Retrain ANN
# ================================
@app.route("/update-jd", methods=["POST"])
@hr_required
def update_jd():
    jd_text = request.form.get("job_description", "")
    save_jd(jd_text)

    try:
        subprocess.run(
            [sys.executable, "ann_trainer.py"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        return f"ANN training failed: {str(e)}", 500

    return redirect(url_for("hr_dashboard"))

# ================================
# Admin Page (Protected)
# ================================
@app.route("/admin")
@admin_required
def admin_page():
    return render_template("admin.html")

# ================================
# Resume Upload
# ================================
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("resume")
    if not file:
        return "No file uploaded", 400

    uid = uuid.uuid4().hex[:8]
    filename = secure_filename(uid + os.path.splitext(file.filename)[1])
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    fuzzy_scores[uid] = calculate_fuzzy_score(file_path)
    ann_scores[uid] = predict_ann_score_from_resume(file_path)

    with open(FUZZY_FILE, "w") as f:
        json.dump(fuzzy_scores, f)

    with open(ANN_FILE, "w") as f:
        json.dump(ann_scores, f)

    return jsonify({"uid": uid})

# ================================
# File Operations
# ================================
@app.route("/download/<uid>")
def download(uid):
    for fname in os.listdir(UPLOAD_FOLDER):
        if fname.startswith(uid):
            return send_from_directory(UPLOAD_FOLDER, fname, as_attachment=True)
    return "File not found", 404

@app.route("/delete/<uid>", methods=["DELETE"])
@hr_required
def delete(uid):
    if uid in scores:
        return jsonify({"error": "Resume already scored. Cannot delete."}), 403

    for fname in os.listdir(UPLOAD_FOLDER):
        if fname.startswith(uid):
            os.remove(os.path.join(UPLOAD_FOLDER, fname))
            break

    for db, path in [
        (scores, SCORES_FILE),
        (fuzzy_scores, FUZZY_FILE),
        (ann_scores, ANN_FILE)
    ]:
        db.pop(uid, None)
        with open(path, "w") as f:
            json.dump(db, f)

    return "", 204

# ================================
# Scores
# ================================
@app.route("/getscore/<uid>")
def get_score(uid):
    return jsonify({
        "score": scores.get(uid, "Not yet scored"),
        "suggested": fuzzy_scores.get(uid, "0"),
        "ann": ann_scores.get(uid, "0")
    })

@app.route("/submitscore/<uid>", methods=["POST"])
@hr_required
def submit_score(uid):
    score = request.get_json().get("score")
    if score is None:
        return "Invalid score", 400

    scores[uid] = score
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f)

    return jsonify({"message": "Score submitted successfully"})

# ================================
# Admin Export
# ================================
@app.route("/export-csv")
@admin_required
def export_csv():
    def generate():
        yield "User ID,Manual Score,Fuzzy Score,ANN Score\n"
        for uid in scores:
            yield f"{uid},{scores.get(uid)},{fuzzy_scores.get(uid,'0')},{ann_scores.get(uid,'0')}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=resume_scores.csv"}
    )

# ================================
# Auth
# ================================
@app.route("/hr-login", methods=["GET", "POST"])
def hr_login():
    if request.method == "POST":
        if request.form.get("passcode") == HR_PASSCODE:
            session["hr_logged_in"] = True
            return redirect(url_for("hr_dashboard"))
        return render_template("hr_login.html", error="Incorrect HR passcode!")
    return render_template("hr_login.html")

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form.get("passcode") == ADMIN_PASSCODE:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_page"))
        return render_template("admin_login.html", error="Incorrect Admin passcode!")
    return render_template("admin_login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ================================
# Run
# ================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)
