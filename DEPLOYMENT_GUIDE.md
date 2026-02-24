# Deployment Instructions for Improved Phishing Detection Model

## Files to Deploy

The following files should be copied to your SSH server at `/opt/dataproject/phishing_websites/`:

```
1. backend.py                      - Updated Flask server (uses new model)
2. url_extract_full.py             - New 30-feature extractor
3. random_forest_full_features.pkl - New trained model (96.5% accuracy)
4. requirements.txt                - Dependencies (ensure tldextract, whois,
   dnspython are included)
5. frontend.py                     - Streamlit frontend (no changes needed)
```

## Deployment Steps

### Option 1: Using SCP (from Linux/Mac)

```bash
# From your local machine
ssh your_user@your_server_ip
cd /opt/dataproject/phishing_websites

# From another terminal, copy files
scp backend.py url_extract_full.py random_forest_full_features.pkl \
    your_user@your_server_ip:/opt/dataproject/phishing_websites/

# Or using rsync for batch copy
rsync -avz ./ your_user@your_server_ip:/opt/dataproject/phishing_websites/
```

### Option 2: Using WinSCP (Windows GUI)

1. Open WinSCP
2. Connect to your server using SSH credentials
3. Navigate to `/opt/dataproject/phishing_websites/`
4. Drag and drop the 5 files listed above

### Option 3: Using SSH Terminal

```bash
# SSH into your server
ssh your_user@your_server_ip

# Navigate to project directory
cd /opt/dataproject/phishing_websites

# Download new files (if stored on GitHub or another server)
# Or paste the content manually into the files

# Update backend.py and url_extract_full.py content
# Place random_forest_full_features.pkl in the project directory
```

## Post-Deployment Setup

### 1. Install Updated Dependencies

```bash
cd /opt/dataproject/phishing_websites
pip install -r requirements.txt

# Ensure these packages are installed:
pip install flask scikit-learn whois dnspython tldextract
```

### 2. Restart Flask Backend Service

```bash
# If using systemd
sudo systemctl restart phishing_backend

# Or if running manually
pkill -f "python backend.py"
python backend.py &
```

### 3. Verify Deployment

```bash
# Test the health endpoint
curl http://localhost:5000/health
# Expected: {"status":"ok"}

# Test a prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.google.com"}'

# Expected: {"label":"legitimate","confidence":0.98...}
```

### 4. Check Logs

```bash
# Monitor Flask output
tail -f /var/log/phishing_backend.log

# Look for:
# ✅ Loaded improved 30-feature model
# Features extraction should work without errors
```

## Testing with Known URLs

After deployment, test with these URLs to verify the upgrade:

### Should be classified as LEGITIMATE:

```
https://www.google.com
https://github.com
https://stackoverflow.com
https://www.amazon.com
```

### Should be classified as PHISHING:

```
http://www.paypaI.com (note: capital I instead of l)
https://secure-paypal-us.com
http://192.168.1.1/login
```

Expected output:

```json
{
  "label": "phishing",
  "confidence": 0.95
}
```

## Rollback Plan

If issues occur with the new model:

```bash
cd /opt/dataproject/phishing_websites

# Revert to old model (7 features)
cp url_features_model.pkl random_forest_full_features.pkl.backup
# Edit backend.py to load url_features_model.pkl directly

# Or restore from git
git restore backend.py
```

## Performance Metrics (Before/After)

| Metric    | Old Model (7 features) | New Model (30 features) | Improvement |
| --------- | ---------------------- | ----------------------- | ----------- |
| Accuracy  | 73.04%                 | 96.47%                  | +23.4%      |
| Precision | 81.66%                 | 96.60%                  | +15.0%      |
| Recall    | 66.53%                 | 97.08%                  | +30.6%      |
| F1-Score  | 73.32%                 | 96.84%                  | +23.5%      |

The new model catches 30% more phishing attempts while maintaining high precision.

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'whois'"

```bash
pip install whois
```

### Issue: "ModuleNotFoundError: No module named 'dns'"

```bash
pip install dnspython
```

### Issue: Slow predictions (>5 seconds)

- WHOIS and DNS queries add ~1-2 seconds per URL
- Add caching layer to avoid repeated lookups
- Consider Redis cache for frequently checked domains

### Issue: Model confidence always "uncertain"

- Verify random_forest_full_features.pkl is in the correct directory
- Check model file size (should be ~15-20 MB)
- Ensure features are extracted in correct order

## Monitoring

Monitor these metrics after deployment:

1. **False Positive Rate**: % of legitimate URLs classified as phishing
2. **False Negative Rate**: % of phishing URLs classified as legitimate
3. **Processing Time**: Average prediction time per URL
4. **Model Confidence**: Distribution of confidence scores

Expected baseline:

- False Positive Rate: <5% (model is 96.6% precise)
- False Negative Rate: <3% (model has 97% recall)
- Processing Time: 2-3 seconds per URL (due to network queries)

## Version Info

- Model Version: 2.0 (30-feature model)
- Training Date: 2024
- Dataset: phishing_websites.csv (11,055 samples)
- Classes: Phishing (-1) vs Legitimate (1)
- Framework: scikit-learn RandomForest

---

**Status**: Ready for production deployment ✅
