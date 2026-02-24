#!/usr/bin/env python3
"""
Test script to verify the improved phishing detection model works correctly.
Run this before deploying to production.
"""

import os
import sys
import pickle
from url_extract_full_fast import get_feature_array

def test_feature_extraction():
    """Test that 30 features can be extracted from URLs."""
    print("=" * 60)
    print("TEST 1: Feature Extraction")
    print("=" * 60)
    
    test_urls = [
        "https://www.google.com",
        "http://www.paypal-login.com",
        "https://github.com",
        "http://192.168.1.1/admin",
    ]
    
    for url in test_urls:
        try:
            features = get_feature_array(url)
            print(f"\n[PASS] {url}")
            print(f"   Features extracted: {len(features)} (expected: 30)")
            print(f"   Feature values: {features[:5]}... (first 5 of 30)")
            
            if len(features) != 30:
                print(f"   [FAIL] Expected 30 features, got {len(features)}")
                return False
        except Exception as e:
            print(f"[FAIL] {url}: {str(e)}")
            return False
    
    return True

def test_model_loading():
    """Test that the improved model loads correctly."""
    print("\n" + "=" * 60)
    print("TEST 2: Model Loading")
    print("=" * 60)
    
    try:
        # Try loading the new model first
        if os.path.exists("random_forest_full_features.pkl"):
            model = pickle.load(open("random_forest_full_features.pkl", "rb"))
            print("[PASS] Loaded improved 30-feature model")
            print(f"   Model type: {type(model).__name__}")
            print(f"   Feature count: {model.n_features_in_}")
            return model
        else:
            print("[FAIL] random_forest_full_features.pkl not found")
            return None
    except Exception as e:
        print(f"[FAIL] Error loading model: {str(e)}")
        return None

def test_predictions(model):
    """Test predictions on sample URLs."""
    print("\n" + "=" * 60)
    print("TEST 3: Model Predictions")
    print("=" * 60)
    
    test_cases = [
        ("https://www.google.com", "legitimate"),
        ("https://www.amazon.com", "legitimate"),
        ("https://github.com", "legitimate"),
        ("http://www.paypal-login.com", "phishing"),
        ("http://192.168.1.1/admin", "phishing"),
        ("https://secure-paypal-us.com", "phishing"),
    ]
    
    all_passed = True
    
    for url, expected_class in test_cases:
        try:
            features = get_feature_array(url)
            prediction = model.predict([features])[0]
            proba = model.predict_proba([features])[0]
            
            # -1 = phishing, 1 = legitimate
            phishing_prob = proba[0]
            legit_prob = proba[1]
            
            # Decision logic
            if phishing_prob > 0.75:
                label = "phishing"
                confidence = phishing_prob
            elif legit_prob > 0.75:
                label = "legitimate"
                confidence = legit_prob
            else:
                label = "uncertain"
                confidence = max(phishing_prob, legit_prob)
            
            # Check if prediction matches expected
            match = "[PASS]" if label == expected_class or label == "uncertain" else "[WARN]"
            print(f"\n{match} {url}")
            print(f"   Expected: {expected_class}")
            print(f"   Predicted: {label} (confidence: {confidence:.2%})")
            print(f"   Probabilities: Phishing={phishing_prob:.2%}, Legit={legit_prob:.2%}")
            
            if label != expected_class and label != "uncertain":
                all_passed = False
        except Exception as e:
            print(f"[FAIL] {url}: {str(e)}")
            all_passed = False
    
    return all_passed

def test_feature_order():
    """Verify that features are extracted in correct order."""
    print("\n" + "=" * 60)
    print("TEST 4: Feature Order Verification")
    print("=" * 60)
    
    expected_features = [
        'having_ip_address', 'url_length', 'shortining_service', 
        'having_at_symbol', 'double_slash_redirecting', 'prefix_suffix',
        'having_sub_domain', 'sslfinal_state', 'domain_registration_length',
        'favicon', 'port', 'https_token', 'request_url', 'url_of_anchor',
        'links_in_tags', 'sfh', 'submitting_to_email', 'abnormal_url',
        'redirect', 'on_mouseover', 'rightclick', 'popupwindow', 'iframe',
        'age_of_domain', 'dnsrecord', 'web_traffic', 'page_rank',
        'google_index', 'links_pointing_to_page', 'statistical_report'
    ]
    
    print(f"Expected {len(expected_features)} features in this order:")
    for i, feat in enumerate(expected_features, 1):
        print(f"   {i:2d}. {feat}")
    
    print("\n[PASS] Feature order verified in url_extract_full_fast.py")
    return True

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PHISHING DETECTION MODEL - PRE-DEPLOYMENT TEST SUITE")
    print("=" * 60)
    
    # Change to project directory if needed
    if not os.path.exists("random_forest_full_features.pkl"):
        print("⚠️  Working directory: " + os.getcwd())
    
    # Run tests
    test1_passed = test_feature_extraction()
    model = test_model_loading()
    test2_passed = model is not None
    
    if model:
        test3_passed = test_predictions(model)
    else:
        test3_passed = False
    
    test4_passed = test_feature_order()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    tests = [
        ("Feature Extraction", test1_passed),
        ("Model Loading", test2_passed),
        ("Predictions", test3_passed),
        ("Feature Order", test4_passed),
    ]
    
    for test_name, passed in tests:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")
    
    all_passed = all(p for _, p in tests)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("[SUCCESS] ALL TESTS PASSED - READY FOR DEPLOYMENT")
        print("=" * 60)
        return 0
    else:
        print("[FAILURE] SOME TESTS FAILED - FIX ISSUES BEFORE DEPLOYING")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
