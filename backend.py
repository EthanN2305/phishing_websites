from flask import Flask, jsonify, request
from sklearn.ensemble import RandomForestClassifier
import pickle
from url_extract import get_feature_array

app = Flask(__name__)

# Use the production-ready model trained on main features
model = pickle.load(open("url_features_model.pkl", "rb"))


@app.post("/predict")
def predict():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "")
    features = get_feature_array(url)
    print(f"Features for {url}: {features}")
    prediction = model.predict([features])
    print(f"Raw prediction: {prediction[0]}")
    
    # Handle both -1/1 and 0/1 label formats
    pred_val = prediction[0]
    if pred_val == -1 or pred_val == 0:
        label = "phishing"
    elif pred_val == 1:
        label = "legitimate"
    else:
        label = "unknown"
    
    print(f"Final label: {label}")
    return jsonify({"label": label})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
