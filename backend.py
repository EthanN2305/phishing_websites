from flask import Flask, jsonify, request
from sklearn.ensemble import RandomForestClassifier
import pickle
from url_extract_full import get_feature_array

app = Flask(__name__)

# Use the improved 30-feature model trained on phishing_websites.csv
try:
    model = pickle.load(open("random_forest_full_features.pkl", "rb"))
    print("✅ Loaded improved 30-feature model")
except FileNotFoundError:
    print("⚠️  Improved model not found, falling back to 7-feature model")
    model = pickle.load(open("url_features_model.pkl", "rb"))


@app.post("/predict")
def predict():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "")
    
    try:
        features = get_feature_array(url)
        print(f"Features for {url}: {features}")
        
        prediction = model.predict([features])
        proba = model.predict_proba([features])[0]
        
        print(f"Raw prediction: {prediction[0]}, Probabilities: phishing={proba[0]:.4f}, legit={proba[1]:.4f}")
        
        # Use probability-based decision
        # proba[0] = prob of -1 (phishing), proba[1] = prob of 1 (legitimate)
        phishing_prob = proba[0]
        legit_prob = proba[1]
        
        # For the improved 30-feature model, use stricter thresholds
        # Only flag as phishing if model is quite confident
        if phishing_prob > 0.75:
            label = "phishing"
            confidence = phishing_prob
        elif legit_prob > 0.75:
            label = "legitimate"
            confidence = legit_prob
        else:
            label = "uncertain"
            confidence = max(phishing_prob, legit_prob)
        
        print(f"Final label: {label} (confidence={confidence:.4f})")
        return jsonify({"label": label, "confidence": confidence})
    
    except Exception as e:
        print(f"❌ Prediction error: {str(e)}")
        return jsonify({"error": str(e), "status": "error"}), 500


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
