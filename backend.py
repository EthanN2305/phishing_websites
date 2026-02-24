from flask import Flask, jsonify, request
from sklearn.ensemble import RandomForestClassifier
import pickle
from url_extract import get_feature_array

app = Flask(__name__)

# Use the improved 7-feature model (better hyperparameters)
try:
    model = pickle.load(open("url_features_model_improved.pkl", "rb"))
    print("✅ Loaded improved 7-feature model")
except FileNotFoundError:
    model = pickle.load(open("url_features_model.pkl", "rb"))
    print("⚠️  Using original 7-feature model (improved version not found)")


@app.post("/predict")
def predict():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "")
    
    try:
        features = get_feature_array(url)
        print(f"\n[SCAN] {url}")
        print(f"  Feature values:")
        feature_names = ["ip_address", "url_length", "shortening", "at_symbol", 
                        "double_slash", "prefix_suffix", "sub_domain", "port", "https_token"]
        for i, (name, val) in enumerate(zip(feature_names, features)):
            print(f"    {i}: {name:20} = {val:2}")
        print(f"  Total features: {len(features)}")
        
        prediction = model.predict([features])
        proba = model.predict_proba([features])[0]
        
        print(f"  Prediction: {prediction[0]}, Proba: phishing={proba[0]:.4f}, legit={proba[1]:.4f}")
        
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
        
        print(f"  Result: {label.upper()} (confidence={confidence:.4f})")
        print()
        return jsonify({"label": label, "confidence": confidence})
    
    except Exception as e:
        print(f"  ERROR: {str(e)}")
        print()
        return jsonify({"error": str(e), "status": "error"}), 500


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
