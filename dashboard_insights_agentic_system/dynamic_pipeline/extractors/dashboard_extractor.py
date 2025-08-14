# dashboard_extractor.py
import logging
from typing import Dict, Any, Optional

from connectors.bi_connector import connect_bi_dashboard
from powerbi_extractor import PowerBIExtractor
from tableau_extractor import TableauExtractor
from ocr_helper import OCRHelper

logger = logging.getLogger(__name__)


class DashboardExtractor:
    """
    Unified entry point for extracting data from BI dashboards (Power BI, Tableau).
    Automatically chooses API, HTML, and/or OCR fallback depending on source/auth type.
    """

    def __init__(self, ocr_helper: Optional[OCRHelper] = None):
        self.ocr = ocr_helper or OCRHelper()
        self.powerbi_extractor = PowerBIExtractor(self.ocr)
        self.tableau_extractor = TableauExtractor(self.ocr)

    def extract_dashboard(self, source: str, auth_type: str, drill_state: Optional[dict] = None, **kwargs) -> Dict[str, Any]:
        """
        Extracts dashboard data from the specified BI source.

        :param source: "powerbi" or "tableau"
        :param auth_type: "private" or "public"
        :param drill_state: dict mapping component names to drill level/state
        :param kwargs: connection & extraction parameters
        :return: dict in unified schema
        """
        try:
            # Step 1 — Connect
            conn = connect_bi_dashboard(source=source, auth_type=auth_type, **kwargs)
            if conn["status"] != "success":
                return self._fail_result(source, auth_type, conn.get("error"))

            # Step 2 — Extract depending on source/auth_type
            result = None
            if source == "powerbi":
                if auth_type == "private":
                    result = self.powerbi_extractor.extract_private_dashboard(
                        session=conn["client"],
                        workspace_id=conn["metadata"].get("workspace_id"),
                        report_id=kwargs.get("report_id"),
                        drill_state=drill_state
                    )
                elif auth_type == "public":
                    result = self.powerbi_extractor.extract_public_dashboard(
                        public_url=kwargs.get("embed_url"),
                        use_ocr=kwargs.get("use_ocr", True),
                        drill_state=drill_state
                    )
            elif source == "tableau":
                if auth_type == "private":
                    result = self.tableau_extractor.extract_private_dashboard(
                        server=conn["client"],
                        view_id=kwargs.get("view_id"),
                        drill_state=drill_state
                    )
                elif auth_type == "public":
                    result = self.tableau_extractor.extract_public_dashboard(
                        public_url=kwargs.get("public_url"),
                        use_ocr=kwargs.get("use_ocr", True),
                        drill_state=drill_state
                    )

            if result is not None:
                # Always return unified schema
                return self._ensure_unified_schema(result, source, auth_type, drill_state)
            else:
                return self._fail_result(source, auth_type, "Unsupported source/auth_type combination.")

        except Exception as e:
            logger.exception("Dashboard extraction failed.")
            return self._fail_result(source, auth_type, str(e))

    @staticmethod
    def _ensure_unified_schema(result: Dict[str, Any], source: str, auth_type: str, drill_state: Optional[dict] = None) -> Dict[str, Any]:
        # Ensure all keys are present for unified schema, including drill_state and highlights for components
        components = result.get("components", [])
        # Add highlights field to each component if not present
        updated_components = []
        for comp in components:
            if isinstance(comp, dict):
                if "highlights" not in comp:
                    comp["highlights"] = []
            updated_components.append(comp)

        unified = {
            "status": result.get("status", "success"),
            "source": source,
            "auth_type": auth_type,
            "tables": result.get("tables", []),
            "kpis": result.get("kpis", []),
            "filters": result.get("filters", []),
            "visuals": result.get("visuals", []),
            "layout": result.get("layout", {}),
            "components": updated_components,
            "html_text": result.get("html_text", ""),
            "drill_state": result.get("drill_state", drill_state or {}),
            "error": result.get("error", None)
        }
        return unified

    @staticmethod
    def _fail_result(source: str, auth_type: str, error: Any) -> Dict[str, Any]:
        return {
            "status": "failed",
            "source": source,
            "auth_type": auth_type,
            "tables": [],
            "kpis": [],
            "filters": [],
            "visuals": [],
            "layout": {},
            "components": [],
            "html_text": "",
            "error": error
        }