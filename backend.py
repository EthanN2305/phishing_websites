from __future__ import annotations

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.post("/predict")
def predict():
    _ = request.get_json(silent=True) or {}
    return jsonify({"message": "hello world"})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
