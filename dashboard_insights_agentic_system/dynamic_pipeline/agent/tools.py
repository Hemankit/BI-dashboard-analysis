"""
dashboard_tools.py
LangChain tools for interacting with BI dashboards (Power BI, Tableau, etc.)
without modifying the layout.
"""

from typing import Optional, Dict, Any
from langchain_core.tools import tool
from dashboard_client import DashboardClient  # The unified dashboard client class

# Global dashboard client instance (must be initialized before tool calls)
_dashboard_client: Optional[DashboardClient] = None


def set_dashboard_client(client: DashboardClient):
    """
    Assign the shared dashboard client used by all tools.
    This must be called before any tool is invoked.
    """
    global _dashboard_client
    _dashboard_client = client


@tool("apply_filter")
def apply_filter(component_name: str, filter_criteria: Dict[str, Any]) -> str:
    if not _dashboard_client:
        return "No dashboard client initialized."
    success = _dashboard_client.apply_filter(component_name, filter_criteria)
    return f"Filter applied to {component_name}: {filter_criteria}" if success else "Failed to apply filter."


@tool("set_slicer_value")
def set_slicer_value(slicer_name: str, value: Any) -> str:
    if not _dashboard_client:
        return "No dashboard client initialized."
    success = _dashboard_client.apply_slicer(slicer_name, value)
    return f"Slicer '{slicer_name}' set to {value}" if success else f"Failed to set slicer '{slicer_name}'."


@tool("drill_down_visual")
def drill_down_visual(visual_name: str, hierarchy_level: str) -> str:
    if not _dashboard_client:
        return "No dashboard client initialized."
    success = _dashboard_client.drill_down(visual_name, hierarchy_level)
    return f"Drilled down on '{visual_name}' to {hierarchy_level}" if success else f"Failed to drill down on '{visual_name}'."


@tool("drill_up_visual")
def drill_up_visual(visual_name: str) -> str:
    if not _dashboard_client:
        return "No dashboard client initialized."
    success = _dashboard_client.drill_up(visual_name)
    return f"Drilled up on '{visual_name}'" if success else f"Failed to drill up on '{visual_name}'."


@tool("highlight_visual_element")
def highlight_visual_element(visual_name: str, element_id: str) -> str:
    if not _dashboard_client:
        return "No dashboard client initialized."
    success = _dashboard_client.highlight_data_point(visual_name, element_id)
    return f"Highlighted element '{element_id}' in '{visual_name}'" if success else f"Failed to highlight element '{element_id}'."


@tool("reset_filters")
def reset_filters(component_name: Optional[str] = None) -> str:
    if not _dashboard_client:
        return "No dashboard client initialized."
    success = _dashboard_client.clear_filter(component_name)
    if success:
        return f"Filters reset for '{component_name}'" if component_name else "All filters reset"
    return f"Failed to reset filters for '{component_name}'" if component_name else "Failed to reset all filters."


@tool("refresh_data")
def refresh_data() -> str:
    if not _dashboard_client:
        return "No dashboard client initialized."
    success = _dashboard_client.refresh_dashboard_data()
    return "Dashboard data refreshed" if success else "Failed to refresh dashboard data"

dashboard_tools = [
    apply_filter,
    set_slicer_value,
    drill_down_visual,
    drill_up_visual,
    highlight_visual_element,
    reset_filters,
    refresh_data
]