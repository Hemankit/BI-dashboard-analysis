import logging
from typing import Dict, Any, Optional

import requests
import tableauserverclient as TSC

logger = logging.getLogger(__name__)


def connect_private_tableau(
    server_url: str,
    pat_name: str,
    pat_secret: str,
    site: Optional[str] = "",
    use_server_version: bool = True,
) -> Dict[str, Any]:
    """
    Sign in to Tableau Server / Tableau Online using a Personal Access Token (PAT).

    Args:
        server_url: e.g. "https://my-tableau-server.com"
        pat_name: personal access token name
        pat_secret: personal access token secret
        site: contentUrl for the site (empty string for default site)
        use_server_version: whether to auto-detect version

    Returns:
        dict: {"status":"success","source":"tableau","server": TSC.Server, "site": site}
              or {"status":"failed","error": "..."}
    """
    try:
        tableau_auth = TSC.PersonalAccessTokenAuth(pat_name, pat_secret, site)
        server = TSC.Server(server_url, use_server_version=use_server_version)

        # Sign in context (keeps session active; caller should sign out when done)
        server.auth.sign_in(tableau_auth)

        # After sign-in you can use server.* methods in extractors
        return {"status": "success", "source": "tableau", "server": server, "site": site}
    except Exception as e:
        logger.exception("Tableau sign-in failed: %s", e)
        return {"status": "failed", "error": str(e)}


def connect_public_tableau(public_url: str) -> Dict[str, Any]:
    """
    Fetch the public Tableau page (Tableau Public). JS must be used to extract KPI/summary values.
    This returns HTML content to be scraped or embedded in a browser for JS extraction.

    Args:
        public_url: e.g. "https://public.tableau.com/views/yourViz"

    Returns:
        dict with raw HTML or failure.
    """
    try:
        resp = requests.get(public_url, timeout=10)
        resp.raise_for_status()
        return {"status": "success", "source": "tableau", "content": resp.text}
    except requests.RequestException as e:
        logger.exception("Failed to fetch public Tableau URL: %s", e)
        return {"status": "failed", "error": str(e)}


def tableau_sign_out(server: TSC.Server) -> None:
    """
    Sign-out helper for Tableau server sessions. Call this when you are done with the server.
    """
    try:
        server.auth.sign_out()
    except Exception as e:
        logger.exception("Tableau sign-out failed: %s", e)