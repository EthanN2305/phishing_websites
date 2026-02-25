"""Test redirect detection"""
from urllib.parse import urlparse
import requests

def follow_redirects(url, max_redirects=5):
    """
    Follow redirects and return the final URL and redirect count.
    Returns: (final_url, redirect_count, redirect_chain, error_message)
    """
    redirect_chain = [url]
    
    try:
        session = requests.Session()
        current_url = url
        for i in range(max_redirects + 1):
            try:
                response = session.head(current_url, timeout=5, allow_redirects=False, verify=False)
                
                if response.status_code in (301, 302, 303, 307, 308):
                    next_url = response.headers.get('Location')
                    if next_url:
                        if not next_url.startswith('http'):
                            base = urlparse(current_url)
                            if next_url.startswith('/'):
                                next_url = f"{base.scheme}://{base.netloc}{next_url}"
                            else:
                                next_url = f"{base.scheme}://{base.netloc}/{next_url}"
                        
                        redirect_chain.append(next_url)
                        current_url = next_url
                else:
                    return current_url, len(redirect_chain) - 1, redirect_chain, None
            except requests.exceptions.RequestException:
                return current_url, len(redirect_chain) - 1, redirect_chain, None
        
        return current_url, len(redirect_chain) - 1, redirect_chain, "too_many_redirects"
    
    except Exception as e:
        return url, 0, [url], None

# Test URLs
test_urls = [
    'https://httpstat.us/302',  # Redirect
    'https://httpstat.us/200',  # Non-redirect
    'https://www.google.com',   # Real site
]

print("Testing Redirect Detection:\n")

for url in test_urls:
    try:
        final_url, redirect_count, chain, error = follow_redirects(url)
        print(f"URL: {url}")
        print(f"  Redirects: {redirect_count}")
        if redirect_count > 0:
            for i, redirect_url in enumerate(chain):
                marker = "→" if i < len(chain) - 1 else "✓"
                print(f"  {marker} {redirect_url}")
        else:
            print(f"  ✓ No redirects")
        if error:
            print(f"  ⚠️  {error}")
        print()
    except Exception as e:
        print(f"URL: {url}")
        print(f"  Error: {e}\n")
