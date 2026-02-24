import requests
import json

urls_to_test = [
    'https://wwwcustomers-mufg.is',
    'https://www.google.com',
    'https://amazon-alert.tk',
    'https://secure-bank.cf',
    'https://www.microsoft.com'
]

print("Testing Backend Predictions:\n")

for url in urls_to_test:
    try:
        response = requests.post('http://localhost:5000/predict', json={'url': url})
        result = response.json()
        label = result.get('label', 'error')
        confidence = result.get('confidence', 'N/A')
        reason = result.get('reason', '(no additional reason)')
        print(f'{url:40} → {label.upper():12} {confidence:.2%} {reason}')
    except Exception as e:
        print(f'{url:40} → ERROR: {str(e)}')
