import re
# bi_connector.py
import logging
from typing import Dict, Any, Optional

from powerbi_connector import connect_private_powerbi, connect_public_powerbi
from tableau_connector import connect_private_tableau, connect_public_tableau

logger = logging.getLogger(__name__)

def connect_bi_dashboard(
    url: str = None,
    source: Optional[str] = None,
    auth_type: str = "public",
    **kwargs
) -> Dict[str, Any]:
    """
    Unified connector for BI dashboards (Power BI / Tableau) with consistent schema.

    Args:
        source: "powerbi" or "tableau"
        auth_type: "private" or "public"
        **kwargs: connection parameters for the chosen connector

    Returns:
        dict:
        {
            "status": "success" | "failed",
            "source": str,
            "auth_type": str,
            "client": object,            # requests.Session for Power BI, TSC.Server for Tableau
            "metadata": dict,            # basic connection metadata
            "connection_info": dict,     # tokens, urls, etc.
            "error": dict | None
        }
    """
    try:
        # If source is not provided, try to detect from URL
        if not source:
            source = detect_bi_source_from_url(url)
        # Add url to kwargs for connector
        kwargs['url'] = url
        if source == "powerbi":
            if auth_type == "private":
                result = connect_private_powerbi(**kwargs)
                return _normalize_result(result, source, auth_type)
            elif auth_type == "public":
                result = connect_public_powerbi(**kwargs)
                return _normalize_result(result, source, auth_type)
            else:
                raise ValueError(f"Unsupported auth_type '{auth_type}' for Power BI")

        elif source == "tableau":
            if auth_type == "private":
                result = connect_private_tableau(**kwargs)
                return _normalize_result(result, source, auth_type)
            elif auth_type == "public":
                result = connect_public_tableau(**kwargs)
                return _normalize_result(result, source, auth_type)
            else:
                raise ValueError(f"Unsupported auth_type '{auth_type}' for Tableau")

        else:
            raise ValueError(f"Unsupported source '{source}'")

    except Exception as e:
        logger.exception("Failed to connect to BI dashboard: %s", e)
        return {
            "status": "failed",
            "source": source,
            "auth_type": auth_type,
            "client": None,
            "metadata": {},
            "connection_info": {},
            "error": {"type": "exception", "message": str(e)},
        }


def _normalize_result(result: Dict[str, Any], source: str, auth_type: str) -> Dict[str, Any]:
    """
    Normalize connector-specific return dict into a consistent schema for the agent.
    """
    if result.get("status") != "success":
        return {
            "status": "failed",
            "source": source,
            "auth_type": auth_type,
            "client": None,
            "metadata": {},
            "connection_info": {},
            "error": result.get("error", {"type": "unknown", "message": "Connection failed"}),
        }

    # Map to unified fields
    client = None
    metadata = {}
    connection_info = {}

    if source == "powerbi":
        client = result.get("session")
        metadata["workspace_id"] = result.get("workspace_id")
        connection_info["access_token"] = result.get("access_token")
        connection_info["token_type"] = "Bearer"

    elif source == "tableau":
        client = result.get("server")
        metadata["site"] = result.get("site")

    return {
        "status": "success",
        "source": source,
        "auth_type": auth_type,
        "client": client,
        "metadata": metadata,
        "connection_info": connection_info,
        "error": None,
    }

def detect_bi_source_from_url(url: str) -> str:
    """
    Detect BI dashboard source from URL.
    Returns 'powerbi', 'tableau', or raises ValueError if unknown.
    """
    if not url:
        raise ValueError("No URL provided for BI source detection.")
    url = url.lower()
    # Power BI patterns
    if "powerbi.com" in url or re.search(r"/powerbi/|/reports/", url):
        return "powerbi"
    # Tableau patterns
    if "tableau.com" in url or re.search(r"/tableau/|/views/", url):
        return "tableau"
    raise ValueError(f"Could not detect BI source from URL: {url}")