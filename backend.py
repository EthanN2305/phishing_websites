from flask import Flask, jsonify, request
from sklearn.ensemble import RandomForestClassifier
import pickle
from url_extract import get_feature_array
from urllib.parse import urlparse
import requests
from requests.exceptions import RequestException, TooManyRedirects

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

def follow_redirects(url, max_redirects=5):
    """
    Follow redirects and return the final URL and redirect count.
    Returns: (final_url, redirect_count, redirect_chain, error_message)
    """
    redirect_chain = [url]
    
    try:
        # Set a low timeout and allow redirects but track them
        session = requests.Session()
        
        # Manually follow redirects to count them
        current_url = url
        for i in range(max_redirects + 1):
            try:
                # Use HEAD request first (faster, no body download)
                response = session.head(current_url, timeout=5, allow_redirects=False)
                
                # Check if it's a redirect
                if response.status_code in (301, 302, 303, 307, 308):
                    next_url = response.headers.get('Location')
                    if next_url:
                        # Handle relative redirects
                        if not next_url.startswith('http'):
                            base = urlparse(current_url)
                            if next_url.startswith('/'):
                                next_url = f"{base.scheme}://{base.netloc}{next_url}"
                            else:
                                next_url = f"{base.scheme}://{base.netloc}/{next_url}"
                        
                        redirect_chain.append(next_url)
                        current_url = next_url
                else:
                    # No more redirects
                    return current_url, len(redirect_chain) - 1, redirect_chain, None
            except RequestException:
                # Network error, stop following
                return current_url, len(redirect_chain) - 1, redirect_chain, None
        
        # If we get here, too many redirects
        return current_url, len(redirect_chain) - 1, redirect_chain, "too_many_redirects"
    
    except Exception as e:
        return url, 0, [url], None

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
        print(f"\n[SCAN] {url}")
        
        # Check for redirects
        final_url, redirect_count, redirect_chain, redirect_error = follow_redirects(url)
        
        if redirect_error == "too_many_redirects":
            print(f"  ⚠️  Excessive redirects detected ({len(redirect_chain)} in chain)")
            for i, redir_url in enumerate(redirect_chain[:5]):  # Show first 5
                print(f"    {i+1}. {redir_url}")
            if len(redirect_chain) > 5:
                print(f"    ... ({len(redirect_chain) - 5} more)")
            print(f"  Result: PHISHING - Link kept redirecting")
            print()
            return jsonify({
                "label": "phishing",
                "confidence": "N/A",
                "message": "Link kept redirecting"
            })
        
        if redirect_count > 0:
            print(f"  ℹ️  URL redirects detected: {redirect_count} redirect(s)")
            for i, redir_url in enumerate(redirect_chain):
                marker = "→" if i < len(redirect_chain) - 1 else "✓"
                print(f"    {marker} {redir_url}")
            print(f"  Analyzing final URL...")
            analysis_url = final_url
        else:
            analysis_url = url
        
        # Check for suspicious indicators on the final URL
        is_suspicious, reason = check_suspicious_indicators(analysis_url)
        if is_suspicious:
            print(f"  ⚠️  {reason}")
            print(f"  Result: PHISHING (flagged by pattern detection)")
            print()
            return jsonify({"label": "phishing", "confidence": 0.95, "reason": reason})
        
        features = get_feature_array(analysis_url)
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
