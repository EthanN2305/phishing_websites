"""
Train a 9-feature model using CSV data - features extractable from URLs only
Features we CAN extract in production:
1. having_ip_address
2. url_length  
3. shortining_service (shortening_service in CSV)
4. having_at_symbol
5. double_slash_redirecting
6. prefix_suffix
7. having_sub_domain
8. port
9. https_token

This uses pre-calculated values from CSV for better quality than our extraction code.
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle

# Load the dataset
df = pd.read_csv('phishing_websites.csv')

# Select only the 9 URL-extractable features
feature_names = [
    'having_ip_address',
    'url_length',
    'shortining_service',  # Note: CSV uses this spelling
    'having_at_symbol',
    'double_slash_redirecting',
    'prefix_suffix',
    'having_sub_domain',
    'port',
    'https_token'
]

print(f"Loading phishing_websites.csv...")
print(f"Dataset shape: {df.shape}")
print(f"Available columns: {df.columns.tolist()}")
print()

# Use only URL-extractable features
X = df[feature_names]
y = df['result']

print(f"Feature matrix shape: {X.shape}")
print(f"Class distribution: {y.value_counts().to_dict()}")
print()

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training set: {X_train.shape}")
print(f"Test set: {X_test.shape}")
print()

# Train Random Forest with good hyperparameters
print(f"Training RandomForest with 9 URL-extractable features...")
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    class_weight='balanced',
    n_jobs=-1
)

model.fit(X_train, y_train)

# Evaluate
train_acc = model.score(X_train, y_train)
test_acc = model.score(X_test, y_test)

print(f"\nTrain Accuracy: {train_acc:.4f}")
print(f"Test Accuracy: {test_acc:.4f}")
print()

# Feature importance
print("Feature Importance:")
for name, importance in zip(feature_names, model.feature_importances_):
    print(f"  {name}: {importance:.4f}")
print()

# Save the model
model_path = 'url_features_model_improved.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model, f)

print(f"✅ Model saved to {model_path}")
print(f"   Copy to url_features_model.pkl after testing")
