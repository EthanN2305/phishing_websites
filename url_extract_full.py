"""
Enhanced feature extractor for 30-feature phishing detection model.
Extracts URL features using WHOIS, DNS, and SSL checks where possible.
Falls back to safe defaults for unavailable features.
"""

import re
from urllib.parse import urlparse
import numpy as np
import socket
import ssl
import dns.resolver
import tldextract
import whois
from datetime import datetime
import ipaddress

# Global DNS resolver with timeout
dns_resolver = dns.resolver.Resolver()
dns_resolver.timeout = 2
dns_resolver.lifetime = 2

def safe_check(func, *args, default=0, **kwargs):
    """Safely execute a function with timeout and fallback to default."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"Warning: Feature extraction error ({func.__name__}): {str(e)[:50]}")
        return default

def having_ip_address(url):
    """Check if URL uses IP address instead of domain name."""
    domain = urlparse(url).hostname
    if not domain:
        return -1
    try:
        ipaddress.ip_address(domain)
        return 1  # Uses IP address (phishing indicator)
    except ValueError:
        return -1  # Uses domain name (legitimate)

def url_length(url):
    """URL length (longer URLs are more suspicious)."""
    if len(url) < 54:
        return 1  # Short URL (legitimate)
    elif len(url) <= 75:
        return 0  # Medium (suspicious)
    else:
        return -1  # Long URL (phishing)

def shortining_service(url):
    """Check if URL uses shortening service."""
    shorteners = ['bit.ly', 'tinyurl.com', 'short.link', 'ow.ly', 'is.gd', 'buff.ly']
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    return 1 if any(s in domain for s in shorteners) else -1

def having_at_symbol(url):
    """Check for @ symbol (phishing indicator)."""
    return 1 if '@' in url else -1

def double_slash_redirecting(url):
    """Check for // after domain (redirect indicator)."""
    if '//' in urlparse(url).path:
        return 1  # Suspicious
    return -1  # Legitimate

def prefix_suffix(url):
    """Check for - in domain name."""
    domain = urlparse(url).hostname
    if domain and '-' in domain:
        return 1  # Suspicious
    return -1  # Legitimate

def having_sub_domain(url):
    """Count subdomain levels."""
    extracted = tldextract.extract(url)
    subdomain_parts = [p for p in extracted.subdomain.split('.') if p]
    
    if len(subdomain_parts) == 0:
        return -1  # No subdomain (legitimate)
    elif len(subdomain_parts) == 1:
        return 0   # One level (suspicious)
    else:
        return 1   # Multiple levels (phishing)

def sslfinal_state(url):
    """Check SSL certificate validity."""
    parsed = urlparse(url)
    domain = parsed.hostname
    
    if not domain:
        return -1
    
    # Skip SSL check if it's clearly not HTTPS
    if not url.startswith('https://'):
        return 1  # No HTTPS, suspicious
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=1) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                # Has valid SSL certificate
                return -1  # HTTPS with valid cert, legitimate
    except (socket.error, ssl.SSLError, socket.timeout):
        # Has HTTPS but may have cert issues; still better than no HTTPS
        return 0  # HTTPS present but cert issues - neutral

def domain_registration_length(url):
    """Check domain registration length using WHOIS."""
    domain = urlparse(url).hostname
    if not domain:
        return -1
    
    try:
        w = whois.whois(domain)
        if hasattr(w, 'expiration_date'):
            exp_date = w.expiration_date
            if isinstance(exp_date, list):
                exp_date = exp_date[0]
            if isinstance(exp_date, datetime):
                days_remaining = (exp_date - datetime.now()).days
                if days_remaining > 365:
                    return -1  # Legitimate (long registration)
                elif days_remaining > 0:
                    return 0   # Medium
                else:
                    return 1   # About to expire (phishing)
        return 0  # Unable to determine
    except:
        return 0  # Default to uncertain

def favicon(url):
    """Check if favicon exists and matches domain."""
    # Simplified: assume legitimate if served from same domain
    return -1

def port(url):
    """Check for unusual port."""
    parsed = urlparse(url)
    port_num = parsed.port
    
    if port_num is None:
        return -1  # Default port (legitimate)
    elif port_num in [80, 443]:
        return -1  # Standard ports (legitimate)
    else:
        return 1   # Unusual port (suspicious)

def https_token(url):
    """Check HTTPS usage."""
    if url.startswith('https://'):
        return -1  # Uses HTTPS (legitimate)
    elif url.startswith('http://'):
        return 1   # No HTTPS (suspicious)
    else:
        return 0   # Unknown protocol (default to suspicious)

def request_url(url):
    """Check if external URLs are requested from page."""
    # This would require page analysis; default to legitimate
    return -1

def url_of_anchor(url):
    """Check ratios of anchor URLs to total URLs."""
    # This would require page analysis; default to legitimate
    return -1

def links_in_tags(url):
    """Check links in tags (Meta, Script, etc.)."""
    # This would require page analysis; default to legitimate
    return -1

def sfh(url):
    """Server Form Handler (requires page analysis)."""
    # This would require page analysis; default to legitimate
    return -1

def submitting_to_email(url):
    """Check if form submits to email."""
    # This would require page analysis; default to legitimate
    return -1

def abnormal_url(url):
    """Check if URL appears abnormal."""
    # Heuristic: check for suspicious patterns
    suspicious_patterns = ['@', '//', '..', '///', 'javascript:', 'data:']
    for pattern in suspicious_patterns:
        if pattern in url:
            return 1
    return -1

def redirect(url):
    """Check for redirects."""
    # Would need to follow redirects; default to safe
    return -1

def on_mouseover(url):
    """Check for onmouseover events."""
    # Would require page analysis; default to safe
    return -1

def rightclick(url):
    """Check for right-click disabled."""
    # Would require page analysis; default to safe
    return -1

def popupwindow(url):
    """Check for popup windows."""
    # Would require page analysis; default to safe
    return -1

def iframe(url):
    """Check for iframes."""
    # Would require page analysis; default to safe
    return -1

def age_of_domain(url):
    """Check domain age."""
    domain = urlparse(url).hostname
    if not domain:
        return -1
    
    try:
        w = whois.whois(domain)
        if hasattr(w, 'creation_date'):
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            if isinstance(creation_date, datetime):
                age_days = (datetime.now() - creation_date).days
                if age_days > 365:
                    return -1  # Old domain (legitimate)
                elif age_days > 180:
                    return 0   # Medium
                else:
                    return 1   # New domain (suspicious)
        return 0
    except:
        return 0

def dnsrecord(url):
    """Check if DNS record exists."""
    domain = urlparse(url).hostname
    if not domain:
        return -1
    
    try:
        answers = dns_resolver.resolve(domain, 'A')
        return -1 if answers else 1  # Has DNS record (legitimate)
    except:
        return 1  # No DNS record (suspicious)

def web_traffic(url):
    """Check web traffic (requires external API; default to safe)."""
    return -1

def page_rank(url):
    """Check Google PageRank (requires API; default to safe)."""
    return -1

def google_index(url):
    """Check if page is indexed by Google (requires API; default to safe)."""
    return -1

def links_pointing_to_page(url):
    """Check number of links pointing to page (requires API; default to safe)."""
    return -1

def statistical_report(url):
    """Check statistical reports about the domain (default to safe)."""
    return -1

def get_feature_array(url):
    """
    Extract all 30 features for the phishing detection model.
    Returns feature array in the correct order.
    """
    features = []
    
    # Extract features in the exact order from phishing_websites.csv
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
    features.append(safe_check(request_url, url, default=-1))
    features.append(safe_check(url_of_anchor, url, default=-1))
    features.append(safe_check(links_in_tags, url, default=-1))
    features.append(safe_check(sfh, url, default=-1))
    features.append(safe_check(submitting_to_email, url, default=-1))
    features.append(safe_check(abnormal_url, url, default=-1))
    features.append(safe_check(redirect, url, default=-1))
    features.append(safe_check(on_mouseover, url, default=-1))
    features.append(safe_check(rightclick, url, default=-1))
    features.append(safe_check(popupwindow, url, default=-1))
    features.append(safe_check(iframe, url, default=-1))
    features.append(safe_check(age_of_domain, url, default=0))
    features.append(safe_check(dnsrecord, url, default=1))
    features.append(safe_check(web_traffic, url, default=-1))
    features.append(safe_check(page_rank, url, default=-1))
    features.append(safe_check(google_index, url, default=-1))
    features.append(safe_check(links_pointing_to_page, url, default=-1))
    features.append(safe_check(statistical_report, url, default=-1))
    
    return features
