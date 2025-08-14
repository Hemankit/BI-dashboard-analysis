# powerbi_extractor.py
import logging
from typing import Dict, Any, Optional

from bs4 import BeautifulSoup

from ocr_helper import OCRHelper

logger = logging.getLogger(__name__)


class PowerBIExtractor:
    """
    Extracts KPI/summary values from Power BI dashboards.
    Supports both API-based (private) and HTML+OCR-based (public) extraction.
    """

    def __init__(self, ocr_helper: Optional[OCRHelper] = None):
        """
        :param ocr_helper: Optional shared OCRHelper instance.
        """
        self.ocr = ocr_helper or OCRHelper()

    def extract_private_dashboard(self, client, workspace_id: str, report_id: str, drill_state: Optional[dict] = None) -> Dict[str, Any]:
        """
        Extracts and structures dashboard data for agent reasoning.
        """
        try:
            url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}"
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()

            # Example breakdown (customize as needed for your API response)
            tables = data.get("tables", {})
            kpis = data.get("kpis", [])
            filters = data.get("filters", {})
            visuals = data.get("visuals", {})
            layout = data.get("layout", {})
            components = {}
            # Build a components dict for agent reasoning
            for table_name, table in tables.items():
                components[table_name] = {
                    "type": "table",
                    "fields": table.get("fields", []),
                    "rows": table.get("rows", []),
                    "highlights": []
                }
            for kpi in kpis:
                components[kpi.get("name", f"kpi_{len(components)+1}")] = {
                    "type": "kpi",
                    "value": kpi.get("value"),
                    "description": kpi.get("description", ""),
                    "highlights": []
                }
            for visual_name, visual in visuals.items():
                components[visual_name] = {
                    "type": "visual",
                    "visual_type": visual.get("type"),
                    "fields": visual.get("fields", []),
                    "metadata": visual.get("metadata", {}),
                    "highlights": []
                }

            return {
                "status": "success",
                "source": "powerbi",
                "auth_type": "private",
                "tables": tables,
                "kpis": kpis,
                "filters": filters,
                "visuals": visuals,
                "layout": layout,
                "components": components,
                "drill_state": drill_state or {},
                "error": None
            }
        except Exception as e:
            logger.exception("Private Power BI extraction failed.")
            return {
                "status": "failed",
                "tables": {},
                "kpis": [],
                "filters": {},
                "visuals": {},
                "layout": {},
                "components": {},
                "error": str(e)
            }

    def extract_public_dashboard(self, embed_url: str, use_ocr: bool = True, drill_state: Optional[dict] = None) -> Dict[str, Any]:
        """
        Extracts and structures public Power BI dashboard content for agent reasoning.
        """
        try:
            from bi_connector import connect_public_powerbi
            conn = connect_public_powerbi(embed_url)
            if conn["status"] != "success":
                return {
                    "status": "failed",
                    "tables": {},
                    "kpis": [],
                    "filters": {},
                    "visuals": {},
                    "layout": {},
                    "components": {},
                    "drill_state": drill_state or {},
                    "error": conn.get("error")
                }

            html_content = conn["content"]
            soup = BeautifulSoup(html_content, "html.parser")


            tables = {}
            kpis = []
            filters = {}
            visuals = {}
            layout = {}
            components = {}

            # --- Parse tables from HTML ---
            for table in soup.find_all("table"):
                headers = [th.get_text(strip=True) for th in table.find_all("th")]
                rows = []
                for tr in table.find_all("tr")[1:]:
                    cells = tr.find_all(["td", "th"])
                    row = [cell.get_text(strip=True) for cell in cells]
                    rows.append(row)
                table_name = f"table_{len(tables)+1}"
                tables[table_name] = {"headers": headers, "rows": rows}
                components[table_name] = {
                    "type": "table",
                    "fields": headers,
                    "rows": rows,
                    "highlights": []
                }

            # --- Parse KPIs from HTML or OCR ---
            if use_ocr:
                ocr_result = self.ocr.extract_from_url(embed_url)
                if ocr_result["status"] == "success":
                    for idx, num in enumerate(ocr_result["numbers"]):
                        kpi_name = f"kpi_{idx+1}"
                        kpis.append({"name": kpi_name, "value": num})
                        components[kpi_name] = {"type": "kpi", "value": num, "highlights": []}
                else:
                    components["ocr_error"] = {"type": "error", "message": ocr_result["error"], "highlights": []}

            # --- Parse filters (dropdowns, inputs) ---
            filter_idx = 1
            for select in soup.find_all("select"):
                options = [opt.get_text(strip=True) for opt in select.find_all("option")]
                filter_name = select.get("name") or f"filter_{filter_idx}"
                filters[filter_name] = options
                components[filter_name] = {
                    "type": "filter",
                    "options": options,
                    "highlights": []
                }
                filter_idx += 1
            for inp in soup.find_all("input"):
                filter_name = inp.get("name") or f"filter_{filter_idx}"
                value = inp.get("value")
                filters[filter_name] = value
                components[filter_name] = {
                    "type": inp.get("type", "input"),
                    "value": value,
                    "highlights": []
                }
                filter_idx += 1

            # --- Parse visuals (images, SVGs) ---
            visual_idx = 1
            for img in soup.find_all("img"):
                visual_name = img.get("alt") or img.get("src") or f"visual_{visual_idx}"
                visuals[visual_name] = {
                    "type": "image",
                    "src": img.get("src"),
                    "alt": img.get("alt")
                }
                components[visual_name] = {
                    "type": "visual",
                    "visual_type": "image",
                    "src": img.get("src"),
                    "alt": img.get("alt"),
                    "highlights": []
                }
                visual_idx += 1
            for svg in soup.find_all("svg"):
                visual_name = f"svg_{visual_idx}"
                visuals[visual_name] = {
                    "type": "svg",
                    "content": str(svg)
                }
                components[visual_name] = {
                    "type": "visual",
                    "visual_type": "svg",
                    "content": str(svg),
                    "highlights": []
                }
                visual_idx += 1

            # --- Parse layout (sections, divs) ---
            layout_sections = []
            for section in soup.find_all(["section", "div"]):
                sec_id = section.get("id") or section.get("class")
                layout_sections.append(sec_id)
            layout["sections"] = layout_sections


            return {
                "status": "success",
                "source": "powerbi",
                "auth_type": "public",
                "tables": tables,
                "kpis": kpis,
                "filters": filters,
                "visuals": visuals,
                "layout": layout,
                "components": components,
                "drill_state": drill_state or {},
                "error": None
            }
        except Exception as e:
            logger.exception("Public Power BI extraction failed.")
            return {
                "status": "failed",
                "tables": {},
                "kpis": [],
                "filters": {},
                "visuals": {},
                "layout": {},
                "components": {},
                "drill_state": drill_state or {},
                "error": str(e)
            }
