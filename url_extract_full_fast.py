"""
Optimized feature extractor for phishing detection.
Uses fast URL syntax extraction; skips slow WHOIS/DNS/SSL checks for real-time predictions.
"""

import re
from urllib.parse import urlparse
import ipaddress
import tldextract

def safe_check(func, *args, default=0, **kwargs):
    """Safely execute a function with fallback default."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        return default

def having_ip_address(url):
    """Check if URL uses IP address instead of domain name."""
    domain = urlparse(url).hostname
    if not domain:
        return -1
    try:
        ipaddress.ip_address(domain)
        return 1  # Uses IP address (phishing)
    except ValueError:
        return -1  # Uses domain name (legitimate)

def url_length(url):
    """URL length heuristic."""
    if len(url) < 54:
        return 1  # Short (legitimate)
    elif len(url) <= 75:
        return 0  # Medium (suspicious)
    else:
        return -1  # Long (phishing)

def shortining_service(url):
    """Check for URL shortening service."""
    shorteners = ['bit.ly', 'tinyurl.com', 'short.link', 'ow.ly', 'is.gd', 'buff.ly']
    domain = urlparse(url).netloc.lower()
    return 1 if any(s in domain for s in shorteners) else -1

def having_at_symbol(url):
    """Check for @ symbol in URL."""
    return 1 if '@' in url else -1

def double_slash_redirecting(url):
    """Check for // redirect in path."""
    return 1 if '//' in urlparse(url).path else -1

def prefix_suffix(url):
    """Check for hyphen in domain."""
    domain = urlparse(url).hostname
    return 1 if domain and '-' in domain else -1

def having_sub_domain(url):
    """Count subdomain levels."""
    extracted = tldextract.extract(url)
    subdomain_parts = [p for p in extracted.subdomain.split('.') if p]
    
    if len(subdomain_parts) == 0:
        return -1  # No subdomain
    elif len(subdomain_parts) == 1:
        return 0   # One level
    else:
        return 1   # Multiple levels

def sslfinal_state(url):
    """Check HTTPS (proxy for SSL)."""
    # Fast check: just look at protocol
    if url.startswith('https://'):
        return -1  # Has HTTPS
    else:
        return 1   # No HTTPS

def domain_registration_length(url):
    """Domain registration length (default conservative)."""
    # Can't check without WHOIS; default to unknown
    return 0

def favicon(url):
    """Favicon presence (assume legitimate for now)."""
    return -1

def port(url):
    """Check for unusual port."""
    parsed = urlparse(url)
    port_num = parsed.port
    
    if port_num is None:
        return -1  # Default port
    elif port_num in [80, 443]:
        return -1  # Standard ports
    else:
        return 1   # Unusual port

def https_token(url):
    """HTTPS usage check."""
    if url.startswith('https://'):
        return -1
    elif url.startswith('http://'):
        return 1
    else:
        return 0

def request_url(url):
    """External URL requests (default neutral)."""
    return 0

def url_of_anchor(url):
    """Anchor URL ratios (default neutral)."""
    return 0

def links_in_tags(url):
    """Links in tags (default neutral)."""
    return 0

def sfh(url):
    """Server form handler (default neutral)."""
    return 0

def submitting_to_email(url):
    """Email submission (default neutral)."""
    return 0

def abnormal_url(url):
    """Check for abnormal patterns."""
    suspicious = ['@', '//', '..', '///', 'javascript:', 'data:']
    return 1 if any(p in url for p in suspicious) else -1

def redirect(url):
    """Redirect check (default neutral)."""
    return 0

def on_mouseover(url):
    """Mouseover events (default neutral)."""
    return 0

def rightclick(url):
    """Right-click disabled (default neutral)."""
    return 0

def popupwindow(url):
    """Popup windows (default neutral)."""
    return 0

def iframe(url):
    """Iframe usage (default neutral)."""
    return 0

def age_of_domain(url):
    """Domain age (default unknown)."""
    return 0

def dnsrecord(url):
    """DNS record (default unknown, assume legitimate if no IP)."""
    domain = urlparse(url).hostname
    try:
        ipaddress.ip_address(domain)
        return 1  # IP address, no DNS
    except:
        return 0  # Likely has DNS record

def web_traffic(url):
    """Web traffic (default neutral since we can't check)."""
    return 0

def page_rank(url):
    """Page rank (default neutral since we can't check)."""
    return 0

def google_index(url):
    """Google index (default neutral since we can't check)."""
    return 0

def links_pointing_to_page(url):
    """Links pointing to page (default neutral since we can't check)."""
    return 0

def statistical_report(url):
    """Statistical report (default neutral since we can't check)."""
    return 0

def get_feature_array(url):
    """
    Extract 30 features for phishing detection model.
    Uses only fast URL syntax analysis; skips slow network checks.
    """
    features = []
    
    features.append(safe_check(having_ip_address, url, default=-1))
    features.append(safe_check(url_length, url, default=0))
    features.append(safe_check(shortining_service, url, default=-1))
    features.append(safe_check(having_at_symbol, url, default=-1))
    features.append(safe_check(double_slash_redirecting, url, default=-1))
    features.append(safe_check(prefix_suffix, url, default=-1))
    features.append(safe_check(having_sub_domain, url, default=-1))
    features.append(safe_check(sslfinal_state, url, default=0))
    features.append(safe_check(domain_registration_length, url, default=0))
    features.append(safe_check(favicon, url, default=-1))
    features.append(safe_check(port, url, default=-1))
    features.append(safe_check(https_token, url, default=1))
    features.append(safe_check(request_url, url, default=0))
    features.append(safe_check(url_of_anchor, url, default=0))
    features.append(safe_check(links_in_tags, url, default=0))
    features.append(safe_check(sfh, url, default=0))
    features.append(safe_check(submitting_to_email, url, default=0))
    features.append(safe_check(abnormal_url, url, default=-1))
    features.append(safe_check(redirect, url, default=0))
    features.append(safe_check(on_mouseover, url, default=0))
    features.append(safe_check(rightclick, url, default=0))
    features.append(safe_check(popupwindow, url, default=0))
    features.append(safe_check(iframe, url, default=0))
    features.append(safe_check(age_of_domain, url, default=0))
    features.append(safe_check(dnsrecord, url, default=0))
    features.append(safe_check(web_traffic, url, default=0))
    features.append(safe_check(page_rank, url, default=0))
    features.append(safe_check(google_index, url, default=0))
    features.append(safe_check(links_pointing_to_page, url, default=0))
    features.append(safe_check(statistical_report, url, default=0))
    
    return features
