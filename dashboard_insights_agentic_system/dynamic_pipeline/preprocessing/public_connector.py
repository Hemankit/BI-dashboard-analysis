import requests
from tableau_api_lib import TableauServerConnection
from tableau_api_lib.utils.querying import get_views_dataframe

def connect_public_dashboard(url: str, source: str = "generic") -> dict:
    """
    Connects to a public dashboard (Power BI, Tableau, or generic).
    
    Args:
        url (str): Public dashboard URL.
        source (str): 'powerbi', 'tableau', or 'generic'.
    
    Returns:
        dict: Response containing raw data or session info.
    """
    if source == "generic":
        # Basic GET request
        response = requests.get(url)
        if response.status_code == 200:
            return {"status": "success", "content": response.text}
        return {"status": "failed", "error": response.status_code}

    elif source == "powerbi":
        # Public Power BI reports are usually embedded via iframe with an embed token
        # Example: using requests for public JSON endpoint if available
        response = requests.get(url)
        if response.status_code == 200:
            return {"status": "success", "content": response.json()}
        return {"status": "failed", "error": response.status_code}

    elif source == "tableau":
        try:
            # Tableau "public" dashboards can often be accessed without auth
            # Using tableau-api-lib for structured queries
            connection = TableauServerConnection(
                {
                    "tableau_prod": {
                        "server": url,
                        "username": None,
                        "password": None,
                        "site": None,
                        "api_version": "3.13"
                    }
                },
                env="tableau_prod"
            )
            # For public, no login is needed, just use the URL
            return {"status": "success", "session": connection}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    else:
        return {"status": "failed", "error": "Unsupported source"}