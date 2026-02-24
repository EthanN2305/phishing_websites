import re
from urllib.parse import urlparse
import numpy as np
import whois
import ipaddress
from datetime import datetime
import dns.resolver
import tldextract
from sklearn.preprocessing import LabelEncoder

def URLLength(url):
    return len(url)
    
def DomainLength(url):
    domain = urlparse(url).hostname
    return len(domain)

#helper
def is_ip(hostname):
    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        return False
    
def IsDomainIP(url):
    domain = urlparse(url).hostname
    if is_ip(domain) == True:
        return 1
    else:
        return 0

def TLD(url):
    extract = url.split('.')[-1]
    return extract

def TLDLength(url):
    extract = url.split('.')[-1]
    return len(extract)

def NoOfSubDomain(url):
    extracted = tldextract.extract(url)
    subdomain_parts = [part for part in extracted.subdomain.split('.') if part]
    return len(subdomain_parts)

def NoOfLettersInURL(url):
    return sum(c.isalpha() for c in url)

def LetterRatioInURL(url):
    return NoOfLettersInURL(url)/len(url)

def NoOfDegitsInURL(url):
    return sum(c.isdigit() for c in url)

def DegitRatioInURL(url):
    return NoOfDegitsInURL(url)/len(url)

def NoOfEqualsInURL(url):
    return url.count('=')

def NoOfQMarkInURL(url):
    return url.count('?')

def NoOfAmpersandInURL(url):
    return url.count('%')

def NoOfOtherSpecialCharsInURL(url):
    return sum(not c.isalnum() for c in url)

def SpacialCharRatioInURL(url):
    return NoOfOtherSpecialCharsInURL(url)/len(url)

def IsHTTPS(url):
    scheme = urlparse(url).scheme
    return 1 if scheme == 'https' else 0

def get_feature_array(url, le: LabelEncoder):
    # url_features = ['URLLength', 'DomainLength', 'IsDomainIP', 'TLD', 'TLDLength', 'NoOfSubDomain',
    #             'NoOfLettersInURL', 'LetterRatioInURL', 'NoOfDegitsInURL', 'DegitRatioInURL', 'NoOfEqualsInURL',
    #             'NoOfQMarkInURL', 'NoOfAmpersandInURL', 'NoOfOtherSpecialCharsInURL', 'SpacialCharRatioInURL']
    features = []
    features.append(URLLength(url)) # Problem
    features.append(DomainLength(url))
    features.append(IsDomainIP(url))
    tld = TLD(url)
    features.append(le.transform([tld])[0])
    features.append(TLDLength(url))
    features.append(NoOfSubDomain(url))
    features.append(NoOfLettersInURL(url)) # Problem
    features.append(NoOfDegitsInURL(url))
    features.append(NoOfEqualsInURL(url))
    features.append(NoOfQMarkInURL(url))
    features.append(NoOfAmpersandInURL(url))
    features.append(NoOfOtherSpecialCharsInURL(url))
    return features