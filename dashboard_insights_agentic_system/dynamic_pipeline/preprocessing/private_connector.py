import requests
from typing import Dict, Any

# Tableau SDK
import tableauserverclient as TSC

# Power BI SDK
from powerbiclient import Report
from powerbiclient.authentication import DeviceCodeLogin

def connect_private_dashboard(url: str, source: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
    """
    Connect to a private Power BI or Tableau dashboard using official APIs.

    Args:
        url (str): Dashboard/Server URL.
        source (str): 'powerbi' or 'tableau'.
        credentials (dict): Authentication info.

    Returns:
        dict: Contains SDK session/client object ready for API calls.
    """

    if source.lower() == "powerbi":
        # Authenticate via Azure AD Device Code Flow (simplest for dev)
        if "access_token" not in credentials:
            # This prompts in terminal for device code entry
            device_auth = DeviceCodeLogin()
            token_details = device_auth.get_access_token()
            credentials["access_token"] = token_details["accessToken"]

        session = requests.Session()
        session.headers.update({
            "Authorization": f"Bearer {credentials['access_token']}",
            "Content-Type": "application/json"
        })

        return {
            "status": "success",
            "source": "powerbi",
            "session": session,
            "access_token": credentials["access_token"],
            # You can later instantiate Report(workspace_id, report_id) with this token
        }

    elif source.lower() == "tableau":
        pat_name = credentials.get("pat_name")
        pat_secret = credentials.get("pat_secret")
        site = credentials.get("site", "")

        if not pat_name or not pat_secret:
            raise ValueError("PAT name and secret are required for Tableau.")

        # Connect via TSC
        tableau_auth = TSC.PersonalAccessTokenAuth(
            pat_name, pat_secret, site
        )
        server = TSC.Server(url, use_server_version=True)

        server.auth.sign_in(tableau_auth)

        return {
            "status": "success",
            "source": "tableau",
            "server": server,
            "site": site
        }

    return {"status": "failed", "error": "Unsupported source"}
