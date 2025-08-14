import json
import os
import requests
from typing import Dict, Any, Optional

def extract_kpi_values(session, dashboard_type: str, dashboard_id: str) -> dict:
    """
    Extract KPI values from a dashboard.

    Args:
        session: Authenticated API session or connection object.
        dashboard_type (str): 'powerbi' or 'tableau'.
        dashboard_id (str): Dashboard/workbook identifier.

    Returns:
        dict: KPI name → value mapping.
    """

    if dashboard_type.lower() == "powerbi":
        # Example endpoint for Power BI
        url = f"https://api.powerbi.com/v1.0/myorg/dashboards/{dashboard_id}/tiles"
        response = session.get(url)
        if response.status_code != 200:
            return {"status": "failed", "error": response.text}

        tiles = response.json().get("value", [])
        kpis = {}
        for tile in tiles:
            title = tile.get("title")
            # Some tiles may have datasets you can query for values
            kpis[title] = tile.get("rowValue", None)  # Placeholder - depends on API shape
        return {"status": "success", "kpis": kpis}

    elif dashboard_type.lower() == "tableau":
        # Read KPI values from backend temp store
        kpi_file = f"/tmp/{dashboard_id}_kpis.json"
        if not os.path.exists(kpi_file):
            return {
                "status": "pending",
                "message": "Awaiting KPI data from Tableau JS API frontend."
            }
        with open(kpi_file, "r") as f:
            kpis = json.load(f)
        return {"status": "success", "kpis": kpis}

    else:
        return {"status": "failed", "error": "Unsupported dashboard type"}


def extract_table_data(connection: Dict[str, Any], table_id: str) -> Dict[str, Any]:
    """
    Fetch structured table data from a dashboard component.
    """
    if connection.get("source") == "powerbi":
        # Find dataset ID from table_id mapping, then run DAX query
        dataset_id = connection.get("dataset_map", {}).get(table_id)
        if not dataset_id:
            return {"status": "failed", "error": "Dataset ID not found"}
        
        url = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/executeQueries"
        payload = {
            "queries": [{"query": f"EVALUATE {table_id}"}]
        }
        response = connection["session"].post(url, json=payload)
        if response.status_code != 200:
            return {"status": "failed", "error": response.text}
        rows = response.json()["results"][0]["tables"][0]["rows"]
        return {"table_id": table_id, "rows": rows}

    elif connection.get("source") == "tableau":
        # If using Tableau REST API
        url = f"{connection['session'].server}/api/3.18/sites/{connection['session'].site_id}/views/{table_id}/data"
        response = connection["session"].get(url, headers={"Accept": "application/json"})
        if response.status_code != 200:
            return {"status": "failed", "error": response.text}
        rows = response.json().get("data", [])
        return {"table_id": table_id, "rows": rows}

    return {"status": "failed", "error": "Unsupported source"}


def extract_chart_series(connection: Dict[str, Any], chart_id: str) -> Dict[str, Any]:
    """
    Fetches series data from a chart (e.g., x-axis, y-axis, legends).

    Args:
        connection (dict): Session object + source info from preprocessing.
        chart_id (str): The ID of the chart component.

    Returns:
        dict: Chart data like {"chart_id": "chart1", "title": "Sales Trend", "series": {...}}
    """
    if connection.get("source") == "powerbi":
        # Power BI API call to fetch chart series
        url = f"https://api.powerbi.com/v1.0/myorg/reports/{chart_id}/series"
        response = connection["session"].get(url)
        if response.status_code != 200:
            return {"status": "failed", "error": response.text}
        chart_data = response.json().get("value", {})
        return {"chart_id": chart_id, "data": chart_data}
    elif connection.get("source") == "tableau":
        # Tableau API call to fetch chart series
        url = f"{connection['session'].server}/api/3.18/sites/{connection['session'].site_id}/views/{chart_id}/series"
        response = connection["session"].get(url)
        if response.status_code != 200:
            return {"status": "failed", "error": response.text}
        chart_data = response.json().get("data", {})
        return {"chart_id": chart_id, "data": chart_data}


def extract_filters(connection: Dict[str, Any], dashboard_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetches active filters/slicers applied to the dashboard.

    Args:
        connection (dict): Session object + source info from preprocessing.
        dashboard_id (str, optional): Dashboard ID for filter scope.

    Returns:
        dict: Active filters and their selected values.
              Example: {"filters": {"Region": "North America", "Year": "2024"}}
    """
    if connection.get("source") == "powerbi":
        # Power BI API call to fetch filters
        url = f"https://api.powerbi.com/v1.0/myorg/reports/{dashboard_id}/filters"
        response = connection["session"].get(url)
        if response.status_code != 200:
            return {"status": "failed", "error": response.text}
        filters = response.json().get("value", [])
        return {"filters": {f["name"]: f["selectedValues"] for f in filters}}
    elif connection.get("source") == "tableau":
        # Tableau API call to fetch filters
        url = f"{connection['session'].server}/api/3.18/sites/{connection['session'].site_id}/views/{dashboard_id}/filters"
        response = connection["session"].get(url)
        if response.status_code != 200:
            return {"status": "failed", "error": response.text}
        filters = response.json().get("data", [])
        return {"filters": {f["name"]: f["selectedValues"] for f in filters}}
    else:
        return {"status": "failed", "error": "Unsupported source"}


def data_extraction_pipeline(connection: Dict[str, Any], structure: Dict[str, Any]) -> Dict[str, Any]:
    """
    End-to-end pipeline:
    1. Iterate over components in the structure
    2. Extract their data values
    3. Return consolidated results

    Args:
        connection (dict): Authenticated connection/session object.
        structure (dict): Metadata returned by structure_extractor.

    Returns:
        dict: Combined extracted data by component type.
    """
    extracted_data = {
        "kpis": {},
        "tables": {},
        "charts": {},
        "filters": {}
    }

    for component in structure.get("components", []):
        comp_type = component.get("type")
        comp_id = component.get("id")
        # Skip if type or ID is missing
        if not comp_type or not comp_id:
            continue

        if comp_type == "kpi":
            kpi_values = extract_kpi_values(connection["session"], connection["source"], comp_id)
            extracted_data["kpis"][comp_id] = kpi_values

        elif comp_type == "table":
            table_data = extract_table_data(connection, comp_id)
            extracted_data["tables"][comp_id] = table_data

        elif comp_type == "chart":
            chart_series = extract_chart_series(connection, comp_id)
            extracted_data["charts"][comp_id] = chart_series

    # Extract filters
    filters = extract_filters(connection, structure.get("dashboard_id"))
    extracted_data["filters"] = filters

    return extracted_data