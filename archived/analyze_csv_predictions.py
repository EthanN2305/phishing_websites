"""
Test model with actual phishing/legitimate URLs from the dataset
to understand real-world prediction patterns.
"""

import pickle
import pandas as pd
from url_extract import get_feature_array

# Load datasets
df = pd.read_csv('phishing_websites.csv')
model = pickle.load(open('url_features_model.pkl', 'rb'))

# We don't have the original URLs in the CSV, so let's verify our feature extraction
# against the CSV feature values

feature_names_csv = [
    'having_ip_address', 'url_length', 'shortining_service',
    'having_at_symbol', 'double_slash_redirecting', 'prefix_suffix',
    'having_sub_domain', 'port', 'https_token'
]

print("="*70)
print("MODEL ANALYSIS - Comparing CSV Features to Extraction")
print("="*70)

# Take sample phishing and legitimate URLs
phishing_df = df[df['result'] == -1].head(5)
legit_df = df[df['result'] == 1].head(5)

print("\n--- PHISHING SAMPLES (from CSV) ---\n")
for idx, (i, row) in enumerate(phishing_df.iterrows()):
    csv_features = row[feature_names_csv].values.astype(int).tolist()
    proba = model.predict_proba([csv_features])[0]
    print(f"Sample {idx+1}:")
    print(f"  CSV Features: {csv_features}")
    print(f"  Model proba: phishing={proba[0]:.4f}, legit={proba[1]:.4f}")
    if proba[1] > 0.90:
        result = f"FALSE POSITIVE (marked legitimate, confidence={proba[1]:.4f})"
    elif proba[0] > 0.50:
        result = f"✓ Correct (marked phishing, confidence={proba[0]:.4f})"
    else:
        result = f"Uncertain (confidence={max(proba):.4f})"
    print(f"  Result: {result}\n")

print("\n--- LEGITIMATE SAMPLES (from CSV) ---\n")
for idx, (i, row) in enumerate(legit_df.iterrows()):
    csv_features = row[feature_names_csv].values.astype(int).tolist()
    proba = model.predict_proba([csv_features])[0]
    print(f"Sample {idx+1}:")
    print(f"  CSV Features: {csv_features}")
    print(f"  Model proba: phishing={proba[0]:.4f}, legit={proba[1]:.4f}")
    if proba[1] > 0.90:
        result = f"✓ Correct (marked legitimate, confidence={proba[1]:.4f})"
    elif proba[0] > 0.50:
        result = f"FALSE NEGATIVE (marked phishing, confidence={proba[0]:.4f})"
    else:
        result = f"Uncertain (confidence={max(proba):.4f})"
    print(f"  Result: {result}\n")

# Overall statistics
print("\n" + "="*70)
print("OVERALL ACCURACY ON DATASET")
print("="*70)

X = df[feature_names_csv]
y = df['result']

# Evaluate with CSV features directly
predictions = model.predict(X)
accuracy = (predictions == y).mean()

print(f"\nModel Accuracy (using CSV features directly): {accuracy:.4f}")
print(f"  Correct: {(predictions == y).sum()}")
print(f"  Total: {len(y)}")

# Check confidence on phishing vs legitimate
phishing_mask = y == -1
legit_mask = y == 1

phishing_proba = model.predict_proba(X[phishing_mask])[:, 0]  # prob of phishing class
legit_proba = model.predict_proba(X[legit_mask])[:, 1]  # prob of legit class

print(f"\nPhishing URLs:")
print(f"  Avg phishing confidence: {phishing_proba.mean():.4f}")
print(f"  Min: {phishing_proba.min():.4f}, Max: {phishing_proba.max():.4f}")
print(f"  Unique values (rounded): {len(set(round(p, 4) for p in phishing_proba))}")

print(f"\nLegitimate URLs:")
print(f"  Avg legit confidence: {legit_proba.mean():.4f}")
print(f"  Min: {legit_proba.min():.4f}, Max: {legit_proba.max():.4f}")
print(f"  Unique values (rounded): {len(set(round(p, 4) for p in legit_proba))}")

print("\n" + "="*70)
