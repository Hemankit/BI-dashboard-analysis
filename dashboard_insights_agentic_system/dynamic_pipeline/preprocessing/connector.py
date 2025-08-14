from .url_validator import is_public_dashboard
from .public_connector import connect_public_dashboard
from .private_connector import connect_private_dashboard
from .credential_manager import get_credentials

def connect_to_dashboard(url: str, source: str = None, credentials: dict = None) -> dict:
    """
    Unified connector for public or private dashboards.
    
    Args:
        url (str): Dashboard URL.
        source (str): 'powerbi' or 'tableau' (only required for private).
        credentials (dict): Optional user credentials.
    
    Returns:
        dict: Connection/session details.
    """
    if is_public_dashboard(url):
        return connect_public_dashboard(url)
    else:
        creds = get_credentials(source, credentials)
        return connect_private_dashboard(url, source, creds)