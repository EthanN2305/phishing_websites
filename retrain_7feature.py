#!/usr/bin/env python3
"""
Quick retrain of 7-feature model using phishing_websites.csv dataset.
This should be much better than the original weak model.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle

# Load dataset
print("Loading phishing_websites.csv...")
data = pd.read_csv('phishing_websites.csv')

# The 7 features we use in url_extract.py
feature_names = [
    'having_ip_address',
    'url_length', 
    'shortining_service',
    'having_at_symbol',
    'double_slash_redirecting',
    'prefix_suffix',
    'having_sub_domain'
]

X = data[feature_names]
y = data['result']  # -1 = phishing, 1 = legitimate

print(f"Dataset shape: {X.shape}")
print(f"Class distribution: {y.value_counts().to_dict()}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set: {X_train.shape}")
print(f"Test set: {X_test.shape}")

# Train with better hyperparameters
print("\nTraining RandomForest...")
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# Evaluate
train_acc = model.score(X_train, y_train)
test_acc = model.score(X_test, y_test)

print(f"\nTrain Accuracy: {train_acc:.4f}")
print(f"Test Accuracy: {test_acc:.4f}")

# Feature importance
importance = model.feature_importances_
print("\nFeature Importance:")
for name, imp in zip(feature_names, importance):
    print(f"  {name}: {imp:.4f}")

# Save model
print("\nSaving to url_features_model_improved.pkl...")
with open('url_features_model_improved.pkl', 'wb') as f:
    pickle.dump(model, f)

print("✅ Done! Replace url_features_model.pkl with this new version.")
