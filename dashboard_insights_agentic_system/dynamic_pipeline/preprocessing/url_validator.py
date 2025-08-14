import requests
from urllib.parse import urlparse

def is_public_dashboard(url: str) -> bool:
    """
    Determines if the dashboard URL points to a public dashboard.
    
    Args:
        url (str): Dashboard URL.
    
    Returns:
        bool: True if public, False if private.
    """
    parsed_url = urlparse(url)

    # Step 1: Check domain and path patterns
    if "public.tableau.com" in parsed_url.netloc:
        return True
    if "app.powerbi.com" in parsed_url.netloc and "/public/report" in parsed_url.path:
        return True

    # Step 2: Try a request and check redirect/auth behavior
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)

        if response.status_code in [401, 403]:
            return False  # requires authentication

        # Look for redirects to login pages
        if any(auth_domain in response.url.lower() for auth_domain in [
            "login.microsoftonline.com",
            "login.live.com",
            "id.tableau.com"
        ]):
            return False

        return True  # Accessible without auth
    except requests.RequestException:
        return False