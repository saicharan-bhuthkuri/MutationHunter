"""
MutationHunter Web Application Prototype
Nature-Inspired Genetic Mutation Biomarker Selection & Glioma Grading
"""

import os
import json
from flask import Flask, render_template, request, jsonify, send_from_directory
from src.predictor import MutationHunterPredictor

app = Flask(__name__)
predictor = None

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

def get_predictor():
    global predictor
    if predictor is None:
        predictor = MutationHunterPredictor()
    return predictor

@app.route("/")
def index():
    # Load benchmark results if available
    benchmark_path = os.path.join("results", "benchmark_results.json")
    results = {}
    if os.path.exists(benchmark_path):
        with open(benchmark_path, "r") as f:
            results = json.load(f)
            
    meta_path = os.path.join("data", "processed", "features_meta.json")
    meta = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            meta = json.load(f)
            
    return render_template("index.html", results=results, meta=meta)

@app.route("/api/predict", methods=["POST", "OPTIONS"])
def predict():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    try:
        data = request.get_json(force=True)
        pred_engine = get_predictor()
        res = pred_engine.predict(data)
        return jsonify({"status": "success", "result": res})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/api/benchmark", methods=["GET"])
def get_benchmark():
    benchmark_path = os.path.join("results", "benchmark_results.json")
    if os.path.exists(benchmark_path):
        with open(benchmark_path, "r") as f:
            return jsonify(json.load(f))
    return jsonify({"status": "pending", "message": "Benchmark running..."}), 202

@app.route("/static/plots/<filename>")
def serve_plot(filename):
    return send_from_directory("static/plots", filename)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
