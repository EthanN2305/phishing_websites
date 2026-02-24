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
        
        # Decision logic: flag phishing more aggressively, require very high confidence for legitimate
        if legit_prob > 0.90:
            # Only mark as legitimate if VERY confident (>90%)
            label = "legitimate"
            confidence = legit_prob
        elif phishing_prob > 0.50:
            # If model leans toward phishing (>50%), flag it as phishing
            # Better safe than sorry with potential phishing
            label = "phishing"
            confidence = phishing_prob
        else:
            # Else it's too close to call - mark uncertain
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
