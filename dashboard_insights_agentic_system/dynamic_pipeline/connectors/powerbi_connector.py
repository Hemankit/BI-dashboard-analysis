# powerbi_connector.py
import logging
from typing import Dict, Any, Optional, List

import requests
import msal  # Microsoft Authentication Library for Python

# configure logger
logger = logging.getLogger(__name__)


def get_access_token_client_credentials(
    tenant_id: str,
    client_id: str,
    client_secret: str,
    scope: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Obtain an Azure AD access token for Power BI using client credentials flow.

    Args:
        tenant_id: Azure AD tenant id.
        client_id: Registered application's client id.
        client_secret: Registered application's client secret.
        scope: list of scopes; default points to Power BI resource scope.

    Returns:
        Dict with keys: {"access_token": str, "expires_in": int, "token_type": "Bearer"} or {"error": ...}
    """
    scope = scope or ["https://analysis.windows.net/powerbi/api/.default"]
    authority = f"https://login.microsoftonline.com/{tenant_id}"

    app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)
    result = app.acquire_token_for_client(scopes=scope)

    if "access_token" in result:
        return {
            "access_token": result["access_token"],
            "expires_in": result.get("expires_in"),
            "token_type": result.get("token_type", "Bearer"),
        }
    else:
        logger.error("Failed to acquire Power BI token: %s", result.get("error_description"))
        return {"error": result}


def connect_private_powerbi(
    workspace_id_or_url: str,
    tenant_id: str,
    client_id: str,
    client_secret: str,
    workspace_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create an authenticated requests.Session for Power BI REST API using client credentials.

    Args:
        workspace_id_or_url: Base URL for Power BI API or workspace URL for context.
        tenant_id/client_id/client_secret: Azure AD app credentials.
        workspace_id: optional workspace (group) id to scope subsequent calls.

    Returns:
        dict: {"status":"success","session": requests.Session(), "access_token": "...", "workspace_id": "..."}
              or {"status":"failed","error": "..."}
    """
    token_resp = get_access_token_client_credentials(tenant_id, client_id, client_secret)
    if "access_token" not in token_resp:
        return {"status": "failed", "error": token_resp}

    access_token = token_resp["access_token"]
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "User-Agent": "DashboardInsightsAgenticSystem/1.0",
        }
    )

    return {
        "status": "success",
        "source": "powerbi",
        "session": session,
        "access_token": access_token,
        "workspace_id": workspace_id,
    }


def connect_public_powerbi(embed_url: str) -> Dict[str, Any]:
    """
    Connect to a public Power BI embed (publish-to-web or public JSON endpoint).
    This is a best-effort fetch; many public dashboards embed data in iframes or JS.

    Args:
        embed_url: public embed or report URL.

    Returns:
        dict: {"status":"success","source":"powerbi","content": "<html...>"} or failed dict
    """
    try:
        resp = requests.get(embed_url, timeout=10)
        resp.raise_for_status()
        return {"status": "success", "source": "powerbi", "content": resp.text}
    except requests.RequestException as e:
        logger.exception("Failed to fetch public Power BI URL: %s", e)
        return {"status": "failed", "error": str(e)}