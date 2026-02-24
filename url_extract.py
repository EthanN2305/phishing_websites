# import requests
# import json
from urllib.parse import urlparse
import ipaddress
import whois
from datetime import datetime
import dns.resolver

def having_ip_address(url):
    # Check if the URL contains an IP address
    # Split url into https://  link  and the rest
    parsed_url = urlparse(url)
    if parsed_url.hostname:
        try:
            ipaddress.ip_address(parsed_url.hostname)
            return -1
        except ValueError:
            return 1
    return 1

def url_length(url):
    if len(url) < 54:
        return 1
    elif 54 <= len(url) <= 75:
        return 0
    else:
        return -1

SHORTENING_SERVICES = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly",
    "buff.ly", "is.gd", "cutt.ly", "rb.gy", "shorte.st",
    "adf.ly", "soo.gd", "v.gd", "bit.do", "mcaf.ee",
    "rebrand.ly"
}

def shortening_service(url):
    parsed = urlparse(url)
    hostname = parsed.netloc.lower()

    # remove port if present
    hostname = hostname.split(":")[0]

    return -1 if hostname in SHORTENING_SERVICES else 1

def having_at_symbol(url):
    return -1 if "@" in url else 1

def double_slash_redirecting(url):
    # Split off protocol
    if "://" in url:
        remainder = url.split("://", 1)[1]
    else:
        remainder = url

    return -1 if "//" in remainder else 1

def prefix_suffix(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return -1 if '-' in domain else 1

def having_sub_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    cnt = domain.count('.')
    if cnt < 3:
        return 1
    elif cnt == 3:
        return 0
    else:
        return -1

def port(url):
    try:
        if urlparse(url).port != None:
            return -1
        else:
            return 1
    except:
        return 1

def https_token(url):
    domain = urlparse(url).netloc
    return -1 if 'https' in domain else 1

#helper for whois to get date
def extract_whois_date(date_field):
    if isinstance(date_field, list):
        return min(date_field)
    if isinstance(date_field, datetime):
        return date_field
    return None

def age_of_domain(url):
    try:
        domain = urlparse(url).netloc
        if domain.startswith("www."):
            domain = domain[4:]

        record = whois.whois(domain)
        creation = extract_whois_date(record.creation_date)

        if creation is None:
            return 0

        age_years = (datetime.now(creation.tzinfo) - creation).days / 365

        if age_years >= 2:
            return 1        
        elif age_years >= 1:
            return 0        
        else:
            return -1       

    except Exception:
        return 0

def dnsrecord(url):
    try:
        domain = urlparse(url).netloc
        if domain.startswith("www."):
            domain = domain[4:]

        dns.resolver.resolve(domain, 'A')
        return 1

    except dns.resolver.NXDOMAIN:
        return -1

    except Exception:
        return 0

def domain_registration_length(url):
    try:
        domain = urlparse(url).netloc
        if not domain:
            return 0
        if domain.startswith("www."):
            domain = domain[4:]

        record = whois.whois(domain)
        expiration = extract_whois_date(record.expiration_date)

        if expiration is None:
            return 0

        remaining_years = (expiration - datetime.now(expiration.tzinfo)).days / 365

        if remaining_years >= 1:
            return 1
        else:
            return -1

    except Exception:
        return 0
    
def get_feature_array(url):
    features = []
    features.append(having_ip_address(url))
    features.append(url_length(url))
    features.append(shortening_service(url))
    features.append(having_at_symbol(url))
    features.append(double_slash_redirecting(url))
    features.append(prefix_suffix(url))
    features.append(having_sub_domain(url))
    features.append(port(url))
    features.append(https_token(url))
    return features