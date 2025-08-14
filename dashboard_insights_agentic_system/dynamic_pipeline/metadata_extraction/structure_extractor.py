from typing import Dict, Any
import tableauserverclient as TSC
def extract_dashboard_structure(connection: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts the structural metadata of the dashboard 
    (sheets, visuals, filters, KPIs, etc.).

    Args:
        connection (dict): Connection dict from private_connector or public_connector.

    Returns:
        dict: Structured metadata about the dashboard.
              Example:
              {
                  "title": "Sales Overview",
                  "components": [
                      {"type": "chart", "id": "chart1", "description": "Sales by Region"},
                      {"type": "kpi", "id": "kpi1", "description": "Total Revenue"}
                  ]
              }
    """
    source = connection.get("source")
    session = connection.get("session")
    extra_info = connection.get("extra_info", {})

    if source == "powerbi":
        return _extract_powerbi_structure(session, extra_info)
    elif source == "tableau":
        return _extract_tableau_structure(session, extra_info)
    else:
        return {"error": "Unsupported source or no connection established."}


def _extract_powerbi_structure(session: Any, extra_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts dashboard structure using Power BI REST API.

    Args:
        session (Any): Authenticated requests.Session for Power BI.
        extra_info (dict): Contains dashboard URL or workspace info.

    Returns:
        dict: Power BI dashboard metadata.
    """
    # Fetch dashboards
    dashboards_resp = session.get("https://api.powerbi.com/v1.0/myorg/dashboards")
    dashboards = dashboards_resp.json().get("value", [])

    # Fetch reports
    reports_resp = session.get("https://api.powerbi.com/v1.0/myorg/reports")
    reports = reports_resp.json().get("value", [])

    # Fetch datasets
    datasets_resp = session.get("https://api.powerbi.com/v1.0/myorg/datasets")
    datasets = datasets_resp.json().get("value", [])

    # Fetch workspaces (groups)
    groups_resp = session.get("https://api.powerbi.com/v1.0/myorg/groups")
    groups = groups_resp.json().get("value", [])

    metadata = {
        "dashboards": [],
        "reports": [],
        "datasets": [],
        "workspaces": [],
    }

    # Process dashboards and their tiles
    for dashboard in dashboards:
        dashboard_id = dashboard["id"]
        tiles_resp = session.get(f"https://api.powerbi.com/v1.0/myorg/dashboards/{dashboard_id}/tiles")
        tiles = tiles_resp.json().get("value", [])
        metadata["dashboards"].append({
            "id": dashboard.get("id"),
            "displayName": dashboard.get("displayName"),
            "webUrl": dashboard.get("webUrl"),
            "tiles": [
                {
                    "id": tile.get("id"),
                    "title": tile.get("title"),
                    "embedUrl": tile.get("embedUrl"),
                    "reportId": tile.get("reportId"),
                    "visualType": tile.get("visualType"),
                }
                for tile in tiles
            ]
        })

    # Process reports
    for report in reports:
        metadata["reports"].append({
            "id": report.get("id"),
            "name": report.get("name"),
            "webUrl": report.get("webUrl"),
            "datasetId": report.get("datasetId"),
            "workspaceId": report.get("workspaceId"),
        })

    # Process datasets
    for dataset in datasets:
        metadata["datasets"].append({
            "id": dataset.get("id"),
            "name": dataset.get("name"),
            "tables": dataset.get("tables", []),
            "webUrl": dataset.get("webUrl"),
        })

    # Process workspaces
    for group in groups:
        metadata["workspaces"].append({
            "id": group.get("id"),
            "name": group.get("name"),
            "type": group.get("type"),
        })

    return metadata


def _extract_tableau_structure(session: Any, extra_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts dashboard structure using Tableau REST API.

    Args:
        session (Any): Authenticated requests.Session for Tableau.
        extra_info (dict): Contains site_id and url for Tableau.

    Returns:
        dict: Tableau dashboard metadata.
    """
    # Fetch all workbooks
    metadata = {
        "workbooks": [],
        "views": [],
        "datasources": [],
        "projects": [],
    }

    all_workbooks, _ = session.workbooks.get()
    for workbook in all_workbooks:
        metadata["workbooks"].append({
            "id": workbook.id,
            "name": workbook.name,
            "project_id": workbook.project_id,
            "webpage_url": workbook.webpage_url,
        })

        # Get views for each workbook
        session.workbooks.populate_views(workbook)
        for view in workbook.views:
            metadata["views"].append({
                "id": view.id,
                "name": view.name,
                "sheet_type": view.sheet_type,
                "content_url": view.content_url,
            })

    # Get all datasources
    all_datasources, _ = session.datasources.get()
    for datasource in all_datasources:
        metadata["datasources"].append({
            "id": datasource.id,
            "name": datasource.name,
            "project_id": datasource.project_id,
            "webpage_url": datasource.webpage_url,
        })

    # Get all projects
    all_projects, _ = session.projects.get()
    for project in all_projects:
        metadata["projects"].append({
            "id": project.id,
            "name": project.name,
            "description": project.description,
        })

    return metadata