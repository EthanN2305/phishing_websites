#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#functions to assign values for URL features
import re
from urllib.parse import urlparse
import whois
import ipaddress
from datetime import datetime
import dns.resolver
import tldextract

def URLLength(url):
    return len(url)
    
def DomainLength(url):
    domain = urlparse(url).hostname
    return len(domain)

def IsDomainIP(url):
    domain = urlparse(url).hostname
    if is_ip(domain) == True:
        return 1
    else:
        return 0

def TLD(url):
    extracted = tldextract.extract(url)
    return extracted.suffix

def TLDLength(url):
    extracted = tldextract.extract(url)
    return len(extracted.suffix)

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
    return url.count('&')

def NoOfOtherSpecialCharsInURL(url):
    return sum(not c.isalnum() for c in url)

def SpacialCharRatioInURL(url):
    return NoOfOtherSpecialCharsInURL(url)/len(url)

def IsHTTPS(url):
    scheme = urlparse(url).scheme
    return 1 if scheme == 'https' else 0

