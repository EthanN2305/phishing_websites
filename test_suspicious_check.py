"""Test the suspicious indicator checks"""
from urllib.parse import urlparse

SUSPICIOUS_TLDS = {
    'is', 'tk', 'ga', 'cf', 'ml', 'top', 'xyz', 'gq', 'party',
    'loan', 'click', 'work', 'pw', 'online', 'site', 'space',
    'trade', 'accountant', 'stream', 'download', 'faith'
}

SPOOFED_BRANDS = {
    'apple', 'amazon', 'google', 'microsoft', 'facebook', 'paypal',
    'netflix', 'bank', 'mufg', 'chase', 'wells', 'citibank', 'boa',
    'hsbc', 'barclays', 'crypto', 'coinbase', 'binance', 'uber',
    'airbnb', 'dropbox', 'slack', 'github', 'linkedin', 'twitter',
    'instagram', 'whatsapp', 'telegram', 'discord', 'reddit'
}

def check_suspicious_indicators(url):
    parsed = urlparse(url)
    hostname = parsed.netloc.lower()
    
    if ':' in hostname:
        hostname = hostname.split(':')[0]
    
    domain_part = hostname.replace('www.', '') if hostname.startswith('www.') else hostname
    
    try:
        tld = domain_part.split('.')[-1]
    except:
        tld = ''
    
    if tld in SUSPICIOUS_TLDS:
        return True, f'Suspicious TLD (.{tld})'
    
    for brand in SPOOFED_BRANDS:
        if brand in domain_part and not domain_part.startswith(brand + '.'):
            return True, f'Brand spoofing detected ({brand})'
    
    return False, None

# Test URLs
test_urls = [
    'https://wwwcustomers-mufg.is',
    'https://www.google.com',
    'https://amazon-support.tk',
    'https://secure-bank.cf'
]

print("Suspicious Indicator Check Results:\n")
for url in test_urls:
    is_phishing, reason = check_suspicious_indicators(url)
    result = 'PHISHING' if is_phishing else 'LEGIT'
    reason_str = f' ({reason})' if reason else ''
    print(f'{url:40} → {result:10}{reason_str}')
