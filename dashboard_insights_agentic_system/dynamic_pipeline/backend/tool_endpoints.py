from fastapi import FastAPI, requests
from typing import Dict, Any, Optional, List
from extractors.dashboard_extractor import DashboardExtractor

app = FastAPI()

extractor = DashboardExtractor()

@app.get("/public_dashboard_state")
async def get_public_dashboard_state(source: str, auth_type: str = "public", **kwargs) -> Dict[str, Any]:
    """
    Returns the current state of the dashboard for Power BI or Tableau.
    """
    # You may need to pass additional connection/extraction parameters via kwargs
    dashboard_data = extractor.extract_dashboard(source=source, auth_type=auth_type, **kwargs)
    return dashboard_data

@app.get("/private_dashboard_state")
async def get_private_dashboard_state(source: str, auth_type: str = "private", **kwargs) -> Dict[str, Any]:
    """
    Returns the current state of the dashboard for Power BI or Tableau using private API.
    """
    # may need to pass additional connection/extraction parameters via kwargs
    dashboard_data = extractor.extract_dashboard(source=source, auth_type=auth_type, **kwargs)
    return dashboard_data

@app.post("/apply_filter")
async def apply_filter(
    component_name: str,
    filter_value: Any,
    source: str,
    auth_type: str = "public",  # <-- Add this!
    **kwargs
) -> Dict[str, Any]:
    """
    Apply a filter to a component in the dashboard.
    """
    dashboard = extractor.extract_dashboard(source=source, auth_type=auth_type, **kwargs)
        # components to filter tables, Charts/visuals, KPIs, slicers, and Cards
    filters = dashboard.get("filters", [])
    filter_found = False
     # Update the selected value for the filter
    for f in filters:
        if f.get("name") == component_name:
            f["selected"] = filter_value
            filter_found = True
            break

    if not filter_found:
        return {"status": "failed", "error": f"Filter {component_name} not found."}
    # updating the dashboard with the new filter value
    dashboard["filters"] = filters

    # Trigger re-extraction with new filter values
    # (Assuming your extractor supports passing filters)
    dashboard = extractor.extract_dashboard(
    source=source,
    auth_type=auth_type,
    filters={f["name"]: f.get("selected") for f in filters if f.get("selected")},
    **kwargs
)
    dashboard["filters"] = filters
    return {"status": "success", "dashboard": dashboard}

@app.post("/apply_slicer")
async def apply_slicer(
    slicer_name: str,
    value: Any,
    source: str,
    auth_type: str = "public",  # <-- Add this!
    **kwargs
) -> Dict[str, Any]:
    """
    Set a slicer value in the dashboard.
    """
    dashboard = extractor.extract_dashboard(source=source, auth_type=auth_type, **kwargs)
    slicers = dashboard.get("slicers", [])
    
    # Find and update the slicer
    for slicer in slicers:
        if slicer.get("name") == slicer_name:
            slicer["selected"] = value
            break
    else:
        return {"status": "failed", "error": f"Slicer {slicer_name} not found."}
    # Update the dashboard with the new slicer value
    dashboard["slicers"] = slicers
    # Trigger re-extraction with new slicer values
    dashboard = extractor.extract_dashboard(
        source=source,
        auth_type=auth_type,
        slicers={s["name"]: s.get("selected") for s in slicers if s.get("selected")},
        **kwargs
    )
    
    return {"status": "success", "dashboard": dashboard}

@app.post("/drill_down")
async def drill_down(
    visual_name: str,
    level: str,
    source: str,
    auth_type: str = "public",  # <-- Add this!
    **kwargs
) -> Dict[str, Any]:
    """
    Drill down into a visual hierarchy.
    """
    dashboard = extractor.extract_dashboard(source=source, auth_type=auth_type, **kwargs)
    visuals = dashboard.get("visuals", {})
    
    
    for visual in visuals.values():
        if visual.get("name") == visual_name:
            if "drill_state" not in visual:
                visual["drill_state"] = []
            visual["drill_state"].append(level)
            break
    else:
        return {"status": "failed", "error": f"Visual {visual_name} not found."}
    # Update the dashboard with the new drill state
    dashboard["visuals"] = visuals
    # Trigger re-extraction with new drill state
    dashboard = extractor.extract_dashboard(source=source, auth_type=auth_type, drill_state={visual_name: visual["drill_state"]}, **kwargs)
    return {"status": "success", "dashboard": dashboard}

@app.post("/drill_up")
async def drill_up(
    visual_name: str,
    source: str,
    auth_type: str = "public",  # <-- Add this!
    **kwargs
) -> Dict[str, Any]:
    """
    Drill up one level in a visual hierarchy.
    """
    dashboard = extractor.extract_dashboard(source=source, auth_type=auth_type, **kwargs)
    visuals = dashboard.get("visuals", {})
    
    for visual in visuals.values():
        if visual.get("name") == visual_name:
            if "drill_state" not in visual:
                visual["drill_state"] = []
            visual["drill_state"].pop() # Remove last level
            break
    else:
        return {"status": "failed", "error": f"Visual {visual_name} not found."}
            # Update the dashboard with the new drill state
    dashboard["visuals"] = visuals
    # Trigger re-extraction with new drill state
    dashboard = extractor.extract_dashboard(source=source, auth_type=auth_type, drill_state={visual_name: visual["drill_state"]}, **kwargs)
    return {"status": "success", "dashboard": dashboard}

@app.post('/highlight_data')
async def highlight_data(
    component_name: str,
    data_point: Any,
    source: str,
    auth_type: str = "public",  # <-- Add this!
    **kwargs
) -> Dict[str, Any]:
    """
    Highlight a specific data point in a visual or table.
    """
    dashboard = extractor.extract_dashboard(source=source, auth_type=auth_type, **kwargs)
    components = dashboard.get("components", [])
    
    for comp in components:
        if comp.get("name") == component_name:
            if "highlights" not in comp:
                comp["highlights"] = []
            comp["highlights"].append(data_point)
            break
    else:
        return {"status": "failed", "error": f"Component {component_name} not found."}
    
    # Update the dashboard with the new highlights
    dashboard["components"] = components
    # Trigger re-extraction with new highlights
    dashboard = extractor.extract_dashboard(
        source=source,
        auth_type=auth_type,
        highlights={comp["name"]: comp.get("highlights") for comp in components if comp.get("highlights")},
        **kwargs
    )

    return {"status": "success", "dashboard": dashboard}

@app.post('/clear_filter')
async def clear_filter(
    component_name: str,
    source: str,
    auth_type: str = "public",  # <-- Add this!
    **kwargs
) -> Dict[str, Any]:
    """
    Clear all filters applied to a specific component.
    """
    dashboard = extractor.extract_dashboard(source=source, auth_type=auth_type, **kwargs)
    components = dashboard.get("components", [])

    for comp in components:
        if comp.get("name") == component_name:
            comp["filters"] = []
            break
    else:
        return {"status": "failed", "error": f"Component {component_name} not found."}

    # Update the dashboard with the cleared filters
    dashboard["components"] = components
    # Trigger re-extraction with cleared filters
    dashboard = extractor.extract_dashboard(
        source=source,
        auth_type=auth_type,
        filters={comp["name"]: comp.get("filters") for comp in components if comp.get("filters")},
        **kwargs
    )

    return {"status": "success", "dashboard": dashboard}

@app.post('/refresh_dashboard')
async def refresh_dashboard(
    source: str,
    auth_type: str = "public",  # <-- Add this
    **kwargs
) -> Dict[str, Any]:
    """
    Refresh the entire dashboard.
    """
    dashboard = extractor.extract_dashboard(source=source, auth_type=auth_type, **kwargs)
    current_filters = {f["name"]: f.get("selected") for f in dashboard.get("filters", []) if f.get("selected")}
    current_drill_state = dashboard.get("drill_state", {})
    current_highlights = {comp["name"]: comp.get("highlights") for comp in dashboard.get("components", []) if comp.get("highlights")}
    dashboard = extractor.extract_dashboard(
    source=source,
    auth_type=auth_type,
    filters=current_filters if current_filters else None,
    drill_state=current_drill_state if current_drill_state else None,
    highlights=current_highlights if current_highlights else None,
    **kwargs
)

    return {"status": "success", "dashboard": dashboard}
    
