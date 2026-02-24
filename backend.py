from flask import Flask, jsonify, request
from sklearn.ensemble import RandomForestClassifier
import pickle
from url_extract import get_feature_array
from urllib.parse import urlparse

app = Flask(__name__)

# Suspicious TLDs commonly used in phishing
SUSPICIOUS_TLDS = {
    'is', 'tk', 'ga', 'cf', 'ml', 'top', 'xyz', 'gq', 'party',
    'loan', 'click', 'work', 'pw', 'online', 'site', 'space',
    'trade', 'accountant', 'stream', 'download', 'faith'
}

# Common brand names that phishers use for spoofing
SPOOFED_BRANDS = {
    'apple', 'amazon', 'google', 'microsoft', 'facebook', 'paypal',
    'netflix', 'bank', 'mufg', 'chase', 'wells', 'citibank', 'boa',
    'hsbc', 'barclays', 'crypto', 'coinbase', 'binance', 'uber',
    'airbnb', 'dropbox', 'slack', 'github', 'linkedin', 'twitter',
    'instagram', 'whatsapp', 'telegram', 'discord', 'reddit'
}

# Use the improved 9-feature model
try:
    model = pickle.load(open("url_features_model_improved.pkl", "rb"))
    print("✅ Loaded improved 9-feature model")
except FileNotFoundError:
    model = pickle.load(open("url_features_model.pkl", "rb"))
    print("⚠️  Using original 9-feature model (improved version not found)")


def check_suspicious_indicators(url):
    """Check for suspicious patterns that suggest phishing"""
    parsed = urlparse(url)
    hostname = parsed.netloc.lower()
    
    # Remove port if present
    if ':' in hostname:
        hostname = hostname.split(':')[0]
    
    # Remove 'www.' prefix for analysis
    domain_part = hostname.replace('www.', '') if hostname.startswith('www.') else hostname
    
    # Extract TLD
    try:
        tld = domain_part.split('.')[-1]
    except:
        tld = ""
    
    # Check for suspicious TLD
    if tld in SUSPICIOUS_TLDS:
        return True, f"Suspicious TLD (.{tld})"
    
    # Check for brand spoofing - brand name in domain without being the primary domain
    # E.g., "customers-bank.is" or "mufg-security.tk" are phishing
    for brand in SPOOFED_BRANDS:
        if brand in domain_part and not domain_part.startswith(brand + '.'):
            # Brand name is present but not as the primary domain owner
            # This suggests spoofing
            return True, f"Brand spoofing detected ({brand})"
    
    # Check for suspicious patterns: "www" directly before other text
    if hostname.startswith('www') and len(hostname) > 4 and hostname[3].isalpha():
        # Check if it looks like "wwwsomething" without proper domain structure
        if hostname.count('.') < 2 or hostname[3:].replace('.', '').find(hostname[:3]) == -1:
            # Suspicious pattern detected
            pass  # Not always phishing, so be lenient
    
    return False, None


@app.post("/predict")
def predict():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "")
    
    try:
        # First check for suspicious indicators
        is_suspicious, reason = check_suspicious_indicators(url)
        if is_suspicious:
            print(f"\n[SCAN] {url}")
            print(f"  ⚠️  {reason}")
            print(f"  Result: PHISHING (flagged by pattern detection)")
            print()
            return jsonify({"label": "phishing", "confidence": 0.95, "reason": reason})
        
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
        
        # Use probability-based decision with adjusted thresholds
        # proba[0] = prob of -1 (phishing), proba[1] = prob of 1 (legitimate)
        phishing_prob = proba[0]
        legit_prob = proba[1]
        
        # Decision logic: More aggressive phishing detection
        # Require 92.5% confidence for legitimate (was 90%)
        # BUT: Also flag URLs with mostly neutral features (close to 50/50) as uncertain
        if legit_prob > 0.925:
            # Only mark as legitimate if VERY confident (>92.5%)
            label = "legitimate"
            confidence = legit_prob
        elif phishing_prob > 0.55:
            # If model leans toward phishing (>55%), flag it as phishing
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
