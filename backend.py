from flask import Flask, jsonify, request
from sklearn.ensemble import RandomForestClassifier
import pickle
from url_extract import get_feature_array

app = Flask(__name__)

# Use the proven 7-feature model (fast and reliable)
# The 30-feature model requires external APIs not available in production
model = pickle.load(open("url_features_model.pkl", "rb"))
print("✅ Loaded 7-feature model (fast, production-ready)")


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
        
        # For the 7-feature model, use aggressive thresholds for safety
        # Require very high confidence for "legitimate", lower threshold for "phishing"
        if phishing_prob > 0.60:
            # Lean toward phishing
            label = "phishing"
            confidence = phishing_prob
        elif legit_prob > 0.90:
            # Only mark as legitimate if very confident
            label = "legitimate"
            confidence = legit_prob
        else:
            # Default to uncertain (requires manual review)
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
