def get_credentials(source: str, credentials: dict = None) -> dict:
    """
    Retrieves and validates credentials for a private dashboard.
    
    Args:
        source (str): 'powerbi' or 'tableau'
        credentials (dict): Provided by user (e.g., username, password, client_id, client_secret).
    
    Returns:
        dict: Validated credentials (tokens, keys, etc.).
    """
    if source == "powerbi":
        return {
            "client_id": credentials.get("client_id"),
            "client_secret": credentials.get("client_secret"),
            "tenant_id": credentials.get("tenant_id"),
            "username": credentials.get("username"),
            "password": credentials.get("password")
        }
    elif source == "tableau":
        return {
            "personal_access_token": credentials.get("token"),
            "site": credentials.get("site"),
            "username": credentials.get("username"),
            "password": credentials.get("password")
        }
    else:
        return {}
    
    
