from flask import Flask, jsonify, request
from sklearn.ensemble import RandomForestClassifier
import pickle
# from url_extract import get_feature_array
from url_extract_extended import get_feature_array

app = Flask(__name__)

# Use the improved model with overfitting fixes
model = pickle.load(open("random_forest_model.pkl", "rb"))
le = pickle.load(open("label_encoder.pkl", "rb"))


@app.post("/predict")
def predict():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "")
    features = get_feature_array(url, le)
    print(features)
    prediction = model.predict([features])
    # prediction is -1 for phishing and 1 for legitimate
    label = "phishing" if prediction[0] == -1 else "legitimate"
    return jsonify({"label": label})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
