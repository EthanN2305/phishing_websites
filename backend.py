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
    proba = model.predict_proba([features])[0]
    
    print(f"Raw prediction: {prediction[0]}, Probabilities: phishing={proba[0]:.4f}, legit={proba[1]:.4f}")
    
    # Use probability-based decision with threshold
    # proba[0] = prob of -1 (phishing), proba[1] = prob of 1 (legitimate)
    phishing_prob = proba[0]
    legit_prob = proba[1]
    
    # Apply threshold: if phishing probability > 5%, flag as phishing
    # if legit probability > 95%, mark as legitimate
    # otherwise, uncertain
    if phishing_prob > 0.05:
        label = "phishing"
        confidence = phishing_prob
    elif legit_prob > 0.95:
        label = "legitimate"
        confidence = legit_prob
    else:
        label = "uncertain"
        confidence = max(phishing_prob, legit_prob)
    
    print(f"Final label: {label} (confidence={confidence:.4f})")
    return jsonify({"label": label, "confidence": confidence})


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
