https://huggingface.co/spaces/CharanBharadhwaj/automated-resume-job-matching
# 🚀 Automated Resume – Job Matching Platform

An AI-powered Resume Screening System that helps HR teams evaluate candidates using **Fuzzy Logic**, **Artificial Neural Networks (ANN)**, and manual HR scoring.

This project provides a complete end-to-end workflow:

✅ Resume upload
✅ Feature extraction & NLP processing
✅ Fuzzy-based JD similarity scoring
✅ ANN-based predictive scoring
✅ HR dashboard with manual evaluation
✅ Admin dashboard with exports
✅ Docker-ready deployment (Hugging Face compatible)

---

## 🧠 Key Features

### 👤 User Module

* Upload resumes (PDF / DOCX / TXT)
* Automatic resume parsing
* AI scoring using:

  * Fuzzy Logic
  * ANN Model

### 🧑‍💼 HR Dashboard

* Secure HR login
* View uploaded resumes
* Submit manual HR scores
* Edit Job Description (JD)
* JD updates trigger ANN retraining automatically

### 🛠 Admin Panel

* Secure admin login
* Export evaluation results (CSV)
* Full control over scoring pipeline

---

## ⚙️ Tech Stack

**Backend**

* Python
* Flask
* Scikit-Learn
* Scikit-Fuzzy
* NLP utilities

**Machine Learning**

* Artificial Neural Network (ANN)
* Genetic Algorithm (feature weighting)
* Fuzzy Logic scoring

**Deployment**

* Docker
* Hugging Face Spaces

---

## 📁 Project Structure

```
├── app.py
├── ann_trainer.py
├── fuzzy_logic.py
├── uploads/
├── templates/
├── static/
├── models/
│   └── ann_model.pkl
├── job_description.txt
├── requirements.txt
└── Dockerfile
```

---

## 🧪 Local Setup (Virtual Environment)

```bash
cd "SOFT COMPUTING"
python -m venv venv
venv\Scripts\activate
pip install "pip<24.1"
pip install -r requirements.txt
```

---

## 🧠 Train ANN Model

ANN requires HR-labelled data.

After submitting HR scores:

```bash
python ann_trainer.py
```

This generates:

```
models/ann_model.pkl
```

---

## ▶️ Run Locally

```bash
python app.py
```

Open:

```
http://localhost:7860
```

---

## 🐳 Run with Docker

Build image:

```bash
docker build -t resume-parser .
```

Run container:

```bash
docker run -p 7860:7860 resume-parser
```

---

## ☁️ Deployment (Hugging Face Space)

This project is configured for **Docker Spaces**.

Steps:

1. Create a new Space (SDK: Docker)
2. Push repository files
3. Hugging Face builds automatically
4. App runs on port **7860**

---

## 🔐 Authentication

| Role  | Passcode |
| ----- | -------- |
| HR    | `hr`     |
| Admin | `admin`  |

(Recommended: Move to environment variables for production)

---

## 📊 Scoring Pipeline

```
Resume Upload
      ↓
Fuzzy Logic Score
      ↓
ANN Prediction
      ↓
HR Manual Score
      ↓
ANN Retraining (on JD update)
```

---

## ⚠️ Important Notes

* ANN requires labelled HR data to train.
* Initial ANN scores may be low until sufficient training samples exist.
* Large model files are included for demonstration purposes.

---

## 👨‍💻 Author

**Charan Bharadhwaj**
Automated Resume – Job Matching Platform

---

## ⭐ Future Improvements

* Async ANN training
* Role-based authentication system
* Live JD preview & versioning
* Improved feature engineering for ANN accuracy
