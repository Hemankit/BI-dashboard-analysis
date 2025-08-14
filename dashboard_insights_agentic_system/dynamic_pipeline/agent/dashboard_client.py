"""
dashboard_client.py
Unified client for interacting with BI dashboards (Power BI, Tableau, etc.)
"""

from typing import Optional, Dict, Any
import requests

class DashboardClient:
    def __init__(self, base_url: str, api_key: str, source: str):
        """
        Args:
            base_url: The root URL for the dashboard server.
            api_key: Authentication token for API requests.
            source: 'powerbi' or 'tableau'.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.source = source.lower()
        self.headers = {"Authorization": f"Bearer {api_key}"}

        # Optionally, initialize a source-specific SDK client here
        if self.source not in ("powerbi", "tableau"):
            raise ValueError(f"Unsupported source: {self.source}")

    # ---------------------------
    # Core dashboard actions
    # ---------------------------
    def get_dashboard_state(self) -> dict:
        endpoint = f"{self.base_url}/{self.source}/latest_dashboard_data"
        resp = requests.get(endpoint, headers=self.headers)
        resp.raise_for_status()
        return resp.json()


    def apply_filter(self, component_name: str, filter_criteria: Dict[str, Any]) -> bool:
        """
        Apply a filter to a component in the dashboard using backend API.
        """
        endpoint = f"{self.base_url}/{self.source}/apply_filter"
        resp = requests.post(endpoint, json={"component": component_name, "filters": filter_criteria}, headers=self.headers)
        if resp.status_code != 200:
            print(f"[ERROR] Failed to apply filter: {resp.text}")
            return False
        print(f"[DEBUG] Applied filter on {component_name} with {filter_criteria}")
        return True

    def apply_slicer(self, slicer_name: str, value: Any) -> bool:
        """
        Set a slicer value using backend API.
        """
        endpoint = f"{self.base_url}/{self.source}/apply_slicer"
        resp = requests.post(endpoint, json={"slicer": slicer_name, "value": value}, headers=self.headers)
        if resp.status_code != 200:
            print(f"[ERROR] Failed to set slicer: {resp.text}")
            return False
        print(f"[DEBUG] Set slicer {slicer_name} to {value}")
        return True

    def drill_down(self, visual_name: str, hierarchy_level: str) -> bool:
        """
        Drill down into a visual hierarchy using backend API.
        """
        endpoint = f"{self.base_url}/{self.source}/drill_down"
        resp = requests.post(endpoint, json={"visual": visual_name, "level": hierarchy_level}, headers=self.headers)
        if resp.status_code != 200:
            print(f"[ERROR] Failed to drill down: {resp.text}")
            return False
        print(f"[DEBUG] Drilled down {visual_name} to level {hierarchy_level}")
        return True

    def drill_up(self, visual_name: str) -> bool:
        """
        Drill up one level in a visual hierarchy using backend API.
        """
        endpoint = f"{self.base_url}/{self.source}/drill_up"
        resp = requests.post(endpoint, json={"visual": visual_name}, headers=self.headers)
        if resp.status_code != 200:
            print(f"[ERROR] Failed to drill up: {resp.text}")
            return False
        print(f"[DEBUG] Drilled up {visual_name}")
        return True

    def highlight_data_point(self, visual_name: str, element_id: str) -> bool:
        """
        Highlight a data point in a visual using backend API.
        """
        endpoint = f"{self.base_url}/{self.source}/highlight_data_point"
        resp = requests.post(endpoint, json={"visual": visual_name, "element_id": element_id}, headers=self.headers)
        if resp.status_code != 200:
            print(f"[ERROR] Failed to highlight data point: {resp.text}")
            return False
        print(f"[DEBUG] Highlighted {element_id} in {visual_name}")
        return True

    def clear_filter(self, component_name: Optional[str] = None) -> bool:
        """
        Clear filter(s) for a component or all components using backend API.
        """
        endpoint = f"{self.base_url}/{self.source}/clear_filter"
        payload = {"component": component_name} if component_name else {}
        resp = requests.post(endpoint, json=payload, headers=self.headers)
        if resp.status_code != 200:
            print(f"[ERROR] Failed to clear filter(s): {resp.text}")
            return False
        target = component_name if component_name else "ALL components"
        print(f"[DEBUG] Cleared filters for {target}")
        return True

    def refresh_dashboard_data(self) -> bool:
        """
        Refresh dashboard data from the source using backend API.
        """
        endpoint = f"{self.base_url}/{self.source}/refresh_dashboard_data"
        resp = requests.post(endpoint, headers=self.headers)
        if resp.status_code != 200:
            print(f"[ERROR] Failed to refresh dashboard data: {resp.text}")
            return False
        print(f"[DEBUG] Refreshed data for {self.source} dashboard")
        return True

    # ---------------------------
    # Source-specific helpers
    # ---------------------------

    # You can add source-specific helpers here if needed, but all main actions should use backend API.