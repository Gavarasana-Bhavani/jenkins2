"""
app.py
Flask web application for the Jenkins Failure Detection & Resolution Dashboard.
Exposes REST API endpoints consumed by the frontend dashboard.
"""
import os, sys, json, pickle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, request, jsonify, render_template
from resolution_engine.resolution_engine import get_resolution, get_all_failure_types

app = Flask(__name__, template_folder="templates")

MODEL_PATH   = os.path.join(os.path.dirname(__file__), "../model/best_model.pkl")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "../model/model_results.json")

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

with open(RESULTS_PATH) as f:
    model_results = json.load(f)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/predict", methods=["POST"])
def predict():
    data     = request.get_json()
    log_text = data.get("log", "").strip()
    if not log_text:
        return jsonify({"error": "No log text provided"}), 400

    prediction = model.predict([log_text])[0]

    try:
        proba      = model.predict_proba([log_text])[0]
        classes    = model.classes_
        confidence = float(max(proba)) * 100
        top_probs  = sorted(
            [{"label": c, "prob": round(float(p) * 100, 1)} for c, p in zip(classes, proba)],
            key=lambda x: x["prob"], reverse=True
        )[:3]
    except Exception:
        confidence = 100.0
        top_probs  = [{"label": prediction, "prob": 100.0}]

    resolution = get_resolution(prediction)
    return jsonify({
        "prediction": prediction,
        "confidence": round(confidence, 1),
        "top_probs":  top_probs,
        "resolution": resolution,
    })


@app.route("/api/model_stats")
def model_stats():
    return jsonify(model_results)


@app.route("/api/failure_types")
def failure_types():
    return jsonify(get_all_failure_types())


if __name__ == "__main__":
    print("[INFO] Starting Jenkins Failure Detection Dashboard...")
    print("[INFO] Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)
