# tableau_extractor.py
import logging
from typing import Dict, Any, Optional

from bs4 import BeautifulSoup
from utils.ocr_helper import OCRHelper

logger = logging.getLogger(__name__)


class TableauExtractor:
    """
    Extracts KPI/summary values from Tableau dashboards.
    Supports both API-based (private) and HTML+OCR-based (public) extraction.
    """

    def __init__(self, ocr_helper: Optional[OCRHelper] = None):
        """
        :param ocr_helper: Optional shared OCRHelper instance.
        """
        self.ocr = ocr_helper or OCRHelper()

    def extract_private_dashboard(self, server, view_id: str, drill_state: Optional[dict] = None) -> Dict[str, Any]:
        """
        Extracts data using the Tableau Server/Online REST API.
        """
        try:
            # Retrieve the view item
            view_item = server.views.get_by_id(view_id)

            # Retrieve CSV data for that view
            server.views.populate_csv(view_item)
            csv_data = view_item.csv

            return {
                "status": "success",
                "source": "tableau",
                "auth_type": "private",
                "data": csv_data,
                "drill_state": drill_state or {},
                "error": None
            }

        except Exception as e:
            logger.exception("Private Tableau extraction failed.")
            return {"status": "failed", "data": {}, "error": str(e)}

    def extract_public_dashboard(self, public_url: str, use_ocr: bool = True, drill_state: Optional[dict] = None) -> Dict[str, Any]:
        """
        Extracts Tableau Public dashboard content via HTML scraping and optional OCR.
        """
        try:
            from dynamic_pipeline.connectors.bi_connector import connect_public_tableau
            conn = connect_public_tableau(public_url)
            if conn["status"] != "success":
                return {"status": "failed", "data": {}, "drill_state": drill_state or {}, "error": conn.get("error")}

            html_content = conn["content"]
            soup = BeautifulSoup(html_content, "html.parser")


            # --- Unified, componentized schema for agent reasoning ---
            extracted_data = {
                "status": "success",
                "source": "tableau",
                "auth_type": "public",
                "tables": [],
                "kpis": [],
                "filters": [],
                "visuals": [],
                "layout": {},
                "components": [],
                "html_text": soup.get_text(separator=" ", strip=True),
                "drill_state": drill_state or {},
                "error": None
            }

            # --- Parse tables ---
            for table in soup.find_all("table"):
                rows = []
                for tr in table.find_all("tr"):
                    cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                    if cells:
                        rows.append(cells)
                if rows:
                    table_obj = {
                        "headers": rows[0] if rows else [],
                        "rows": rows[1:] if len(rows) > 1 else []
                    }
                    extracted_data["tables"].append(table_obj)
                    extracted_data["components"].append({
                        "type": "table",
                        "headers": table_obj["headers"],
                        "rows": table_obj["rows"],
                        "highlights": []
                    })

            # --- Parse KPIs (from OCR or heuristics) ---
            if use_ocr:
                ocr_result = self.ocr.extract_from_url(public_url)
                if ocr_result["status"] == "success":
                    extracted_data["kpis"] = ocr_result.get("numbers", [])
                    for idx, num in enumerate(extracted_data["kpis"]):
                        extracted_data["components"].append({
                            "type": "kpi",
                            "name": f"kpi_{idx+1}",
                            "value": num,
                            "highlights": []
                        })
                else:
                    extracted_data["error"] = f"OCR failed: {ocr_result['error']}"
            else:
                # Heuristic: look for numbers in prominent tags
                kpi_candidates = []
                for tag in soup.find_all(["h1", "h2", "h3", "span", "div"]):
                    text = tag.get_text(strip=True)
                    if text and any(char.isdigit() for char in text):
                        kpi_candidates.append(text)
                extracted_data["kpis"] = kpi_candidates
                for idx, num in enumerate(kpi_candidates):
                    extracted_data["components"].append({
                        "type": "kpi",
                        "name": f"kpi_{idx+1}",
                        "value": num,
                        "highlights": []
                    })

            # --- Parse filters (heuristic: dropdowns, input fields) ---
            for select in soup.find_all("select"):
                options = [opt.get_text(strip=True) for opt in select.find_all("option")]
                filter_obj = {
                    "type": "dropdown",
                    "options": options
                }
                extracted_data["filters"].append(filter_obj)
                extracted_data["components"].append({
                    "type": "filter",
                    "filter_type": "dropdown",
                    "options": options,
                    "highlights": []
                })
            for inp in soup.find_all("input"):
                filter_obj = {
                    "type": inp.get("type", "input"),
                    "name": inp.get("name"),
                    "value": inp.get("value")
                }
                extracted_data["filters"].append(filter_obj)
                extracted_data["components"].append({
                    "type": "filter",
                    "filter_type": inp.get("type", "input"),
                    "name": inp.get("name"),
                    "value": inp.get("value"),
                    "highlights": []
                })

            # --- Parse visuals (heuristic: images, svg, charts) ---
            for img in soup.find_all("img"):
                visual_obj = {
                    "type": "image",
                    "src": img.get("src"),
                    "alt": img.get("alt")
                }
                extracted_data["visuals"].append(visual_obj)
                extracted_data["components"].append({
                    "type": "visual",
                    "visual_type": "image",
                    "src": img.get("src"),
                    "alt": img.get("alt"),
                    "highlights": []
                })
            for svg in soup.find_all("svg"):
                visual_obj = {
                    "type": "svg",
                    "content": str(svg)
                }
                extracted_data["visuals"].append(visual_obj)
                extracted_data["components"].append({
                    "type": "visual",
                    "visual_type": "svg",
                    "content": str(svg),
                    "highlights": []
                })

            # --- Parse layout (basic: sections, divs, grid) ---
            layout = {}
            sections = soup.find_all(["section", "div"])
            layout["sections"] = [sec.get("id") or sec.get("class") for sec in sections]
            extracted_data["layout"] = layout
            extracted_data["components"].append({
                "type": "layout",
                "sections": layout["sections"],
                "highlights": []
            })

            # --- Parse components (heuristic: dashboard widgets) ---
            for widget in soup.find_all(["div", "section"]):
                comp = {
                    "id": widget.get("id"),
                    "class": widget.get("class"),
                    "text": widget.get_text(strip=True),
                    "highlights": []
                }
                extracted_data["components"].append(comp)

            return extracted_data

        except Exception as e:
            logger.exception("Public Tableau extraction failed.")
            return {"status": "failed", "data": {}, "drill_state": drill_state or {}, "error": str(e)}