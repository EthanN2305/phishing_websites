"""
Test the updated model to verify it produces different confidence scores
for different URLs (resolves the identical confidence issue).
"""

import pickle
from url_extract import get_feature_array

# Load the 9-feature model trained on CSV data
model = pickle.load(open('url_features_model.pkl', 'rb'))

test_urls = [
    # Phishing URLs (from dataset context)
    ("http://192.168.1.1/notification", "phishing (IP address)"),
    ("http://bit.ly/a1b2c3", "phishing (shortening service)"),
    ("http://site@domain.com", "phishing (@ symbol)"),
    ("http://genuine-bank.fake-domain.com", "phishing (subdomain mimicry)"),
    ("http://amazon@@--service.com", "phishing (double @, hyphens)"),
    ("http://google.com-update.xyz", "phishing (prefix/suffix trick)"),
    
    # Legitimate URLs
    ("https://www.google.com", "legitimate"),
    ("https://www.amazon.com", "legitimate"),
    ("https://www.github.com/python/cpython", "legitimate"),
    ("https://stackoverflow.com/questions", "legitimate"),
]

print("="*70)
print("PHISHING DETECTION MODEL TEST")
print("="*70)

confidences = []

for url, description in test_urls:
    features = get_feature_array(url)
    prediction = model.predict([features])[0]
    proba = model.predict_proba([features])[0]
    
    # proba[0] = phishing, proba[1] = legitimate
    phishing_prob = proba[0]
    legit_prob = proba[1]
    
    # Determine label based on thresholds
    if legit_prob > 0.90:
        label = "LEGITIMATE"
        confidence = legit_prob
    elif phishing_prob > 0.50:
        label = "PHISHING"
        confidence = phishing_prob
    else:
        label = "UNCERTAIN"
        confidence = max(phishing_prob, legit_prob)
    
    confidences.append((url, label, confidence))
    
    print(f"\n✓ {description}")
    print(f"  URL: {url}")
    print(f"  Features: {features}")
    print(f"  Raw proba: phishing={phishing_prob:.4f}, legit={legit_prob:.4f}")
    print(f"  → {label:12} (confidence: {confidence:.4f})")


print("\n" + "="*70)
print("ANALYSIS")
print("="*70)

# Check if we have good variance in confidence scores
phishing_scores = [c[2] for c in confidences[:6]]
legit_scores = [c[2] for c in confidences[6:]]

print(f"\nPhishing URL confidence scores: {[f'{s:.4f}' for s in phishing_scores]}")
print(f"  Min: {min(phishing_scores):.4f}, Max: {max(phishing_scores):.4f}")
print(f"  Unique values: {len(set(round(s, 4) for s in phishing_scores))}")

print(f"\nLegitimate URL confidence scores: {[f'{s:.4f}' for s in legit_scores]}")
print(f"  Min: {min(legit_scores):.4f}, Max: {max(legit_scores):.4f}")
print(f"  Unique values: {len(set(round(s, 4) for s in legit_scores))}")

# Check if identical confidence issue is fixed
all_phishing_identical = len(set(round(s, 4) for s in phishing_scores)) == 1
if all_phishing_identical:
    print(f"\n⚠️  ISSUE PERSISTS: All phishing URLs have identical confidence!")
else:
    print(f"\n✅ ISSUE RESOLVED: Phishing URLs have different confidence scores!")

print("\n" + "="*70)
