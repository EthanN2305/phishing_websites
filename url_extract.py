# import requests
# import json
from urllib.parse import urlparse
import ipaddress

def having_ip_address(url):
    # Check if the URL contains an IP address
    # Split url into https://  link  and the rest
    parsed_url = urlparse(url)
    if parsed_url.hostname:
        try:
            ipaddress.ip_address(parsed_url.hostname)
            return 1
        except ValueError:
            return -1
    return -1

def url_length(url):
    if len(url) < 54:
        return -1
    elif 54 <= len(url) <= 75:
        return 0
    else:
        return 1

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

    return 1 if hostname in SHORTENING_SERVICES else -1
    
def having_at_symbol(url):
    return 1 if "@" in url else -1

def double_slash_redirecting(url):
    # Split off protocol
    if "://" in url:
        remainder = url.split("://", 1)[1]
    else:
        remainder = url

    return 1 if "//" in remainder else -1

def prefix_suffix(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return 1 if '-' in domain else -1

def having_sub_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    cnt = domain.count('.')
    if cnt < 3:
        return -1
    elif cnt == 3:
        return 0
    else:
        return 1
    
def get_feature_array(url):
    features = []
    features.append(having_ip_address(url))
    features.append(url_length(url))
    features.append(shortening_service(url))
    features.append(having_at_symbol(url))
    features.append(double_slash_redirecting(url))
    features.append(prefix_suffix(url))
    features.append(having_sub_domain(url))
    return features