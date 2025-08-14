import re
from collections import Counter
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from pandas import json_normalize


class DataCleaner:
    def clean_unified_dashboard_data(self, extracted: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cleans and standardizes each component of the unified dashboard schema.
        Returns a dict with cleaned DataFrames or lists for each component type.
        """
        cleaned = {
            "tables": [],
            "kpis": [],
            "filters": [],
            "visuals": [],
            "layout": {},
            "components": [],
            "html_text": extracted.get("html_text", ""),
            "error": extracted.get("error", None),
            "source": extracted.get("source", ""),
            "auth_type": extracted.get("auth_type", ""),
            # Pass through drill_state if present
            "drill_state": extracted.get("drill_state", {})
        }

        # --- Clean tables ---
        for table in extracted.get("tables", []):
            if isinstance(table, dict):
                headers = table.get("headers", [])
                rows = table.get("rows", [])
                df = pd.DataFrame(rows, columns=headers) if headers and rows else pd.DataFrame(rows)
                df = self.clean(df)
                cleaned["tables"].append(df)
            else:
                cleaned["tables"].append(table)

        # --- Clean KPIs ---
        for kpi in extracted.get("kpis", []):
            if isinstance(kpi, dict):
                df = pd.DataFrame([kpi])
                df = self.clean(df)
                cleaned["kpis"].append(df)
            else:
                cleaned["kpis"].append(kpi)

        # --- Clean filters ---
        for filt in extracted.get("filters", []):
            if isinstance(filt, dict):
                df = pd.DataFrame([filt])
                df = self.clean(df)
                cleaned["filters"].append(df)
            else:
                cleaned["filters"].append(filt)

        # --- Clean visuals ---
        for vis in extracted.get("visuals", []):
            if isinstance(vis, dict):
                df = pd.DataFrame([vis])
                df = self.clean(df)
                cleaned["visuals"].append(df)
            else:
                cleaned["visuals"].append(vis)

        # --- Clean components ---
        for comp in extracted.get("components", []):
            if isinstance(comp, dict):
                # Ensure highlights field is present
                if "highlights" not in comp:
                    comp["highlights"] = []
                # Try to infer type and clean accordingly
                comp_type = comp.get("type", "unknown")
                # Clean tabular/structured components, preserve highlights and drill_state
                if comp_type in ["table", "kpi", "filter", "visual"]:
                    # Exclude highlights and drill_state from DataFrame, add back after cleaning
                    highlights = comp.pop("highlights", [])
                    drill_state = comp.pop("drill_state", None)
                    df = pd.DataFrame([comp])
                    df = self.clean(df)
                    comp_cleaned = df.to_dict(orient="records")[0]
                    comp_cleaned["highlights"] = highlights
                    if drill_state is not None:
                        comp_cleaned["drill_state"] = drill_state
                    cleaned["components"].append(comp_cleaned)
                else:
                    cleaned["components"].append(comp)
            else:
                cleaned["components"].append(comp)

        # --- Clean layout ---
        cleaned["layout"] = extracted.get("layout", {})

        return cleaned
    """
    Cleans and standardizes heterogeneous dashboard data extracted from BI tools.
    """

    def __init__(
        self,
        semantic_map: Optional[Dict[str, List[str]]] = None,
        synonym_map: Optional[Dict[str, str]] = None,
        missing_value_strategy: str = "drop",
        fill_constant: Any = 0,
    ):
        """
        :param semantic_map: Mapping from standardized column names to aliases.
        :param synonym_map: Mapping for normalizing categorical values.
        :param missing_value_strategy: Strategy for missing values ('drop', 'fill_mean', 'fill_constant').
        :param fill_constant: Value to use for 'fill_constant' strategy.
        """
        self.semantic_map = semantic_map or {
            "revenue_usd": ["revenue_$", "sales_usd", "total_sales"],
            "date": ["order_date", "created_on", "timestamp"],
        }
        self.synonym_map = synonym_map or {
            "yes": "affirmative",
            "no": "negative",
            "n/a": "not_applicable",
        }
        self.missing_value_strategy = missing_value_strategy
        self.fill_constant = fill_constant

    # ------------------------
    # Core cleaning steps
    # ------------------------

    def flatten_data(self, data: Any) -> List[Dict[str, Any]]:
        """
        Recursively flattens nested dict/list structures into a list of dicts.
        """
        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return [d for item in data for d in self.flatten_data(item)]
        else:
            return [{"value": data}]

    def normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardizes and deduplicates column names.
        """
        # Lowercase, strip spaces, replace non-alphanumeric with underscores
        cols = [
            re.sub(r"[^0-9a-zA-Z_]+", "_", col.strip().lower())
            for col in df.columns
        ]
        # Collapse multiple underscores and strip edges
        cols = [re.sub(r"_+", "_", c).strip("_") for c in cols]
        # Deduplicate
        cols = self._deduplicate_columns(cols)
        # Apply semantic mapping
        reverse_map = {alias: std for std, aliases in self.semantic_map.items() for alias in aliases}
        cols = [reverse_map.get(c, c) for c in cols]

        df.columns = cols
        return df

    def _deduplicate_columns(self, columns: List[str]) -> List[str]:
        counts = Counter()
        new_cols = []
        for col in columns:
            counts[col] += 1
            new_cols.append(f"{col}_{counts[col]}" if counts[col] > 1 else col)
        return new_cols

    def convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converts string columns to appropriate numeric or datetime types where possible.
        """
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_datetime64_any_dtype(df[col]):
                continue

            if pd.api.types.is_string_dtype(df[col]):
                non_null_vals = df[col].dropna().astype(str)
                if non_null_vals.empty:
                    continue

                if non_null_vals.str.match(r"\d{4}-\d{1,2}-\d{1,2}").mean() > 0.8:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                elif non_null_vals.str.match(r"^-?\d+(\.\d+)?$").mean() > 0.8:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                else:
                    df[col] = df[col].astype(str)
        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handles missing values according to the configured strategy.
        """
        if self.missing_value_strategy == "drop":
            return df.dropna()
        elif self.missing_value_strategy == "fill_mean":
            for col in df.select_dtypes(include=["number"]).columns:
                df[col].fillna(df[col].mean(), inplace=True)
            for col in df.select_dtypes(include=["object"]).columns:
                if not df[col].mode().empty:
                    df[col].fillna(df[col].mode()[0], inplace=True)
            return df
        elif self.missing_value_strategy == "fill_constant":
            return df.fillna(self.fill_constant)
        else:
            raise ValueError(f"Unsupported missing value strategy: {self.missing_value_strategy}")

    def normalize_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalizes numeric and percentage formats.
        """
        for col in df.select_dtypes(include=["object", "string"]).columns:
            series = df[col].astype(str).str.strip()
            is_percentage = series.str.contains("%").mean() > 0.5

            # Remove currency, commas, %
            cleaned = series.str.replace(r"[\$,]", "", regex=True).str.replace("%", "", regex=True)
            numeric_series = pd.to_numeric(cleaned, errors="coerce")

            if is_percentage:
                numeric_series = numeric_series / 100.0

            df[col] = numeric_series.fillna(df[col])
        return df

    def standardize_categories(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardizes categorical string values.
        """
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].str.lower().str.strip().replace(self.synonym_map)
        return df

    def parse_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converts date-like strings to datetime objects.
        """
        for col in df.select_dtypes(include=["object", "string"]).columns:
            try:
                parsed = pd.to_datetime(df[col], errors="coerce")
                if parsed.notnull().sum() > 0:
                    df[col] = parsed
            except Exception:
                pass
        return df

    def summarize_dataset(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Produces a summary of the dataframe.
        """
        summary = {"row_count": len(df), "columns": {}}
        for col in df.columns:
            col_info = {
                "dtype": str(df[col].dtype),
                "unique_count": df[col].nunique(),
                "null_count": df[col].isnull().sum(),
            }
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info["min"] = df[col].min()
                col_info["max"] = df[col].max()
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                col_info["min_date"] = df[col].min()
                col_info["max_date"] = df[col].max()
            summary["columns"][col] = col_info
        return summary

    def convert_extracted_data_to_dataframes(self, extracted: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts unified extracted dashboard data into cleaned DataFrames for each component type.
        """
        return self.clean_unified_dashboard_data(extracted)

    def _infer_component_type(self, name: str) -> str:
        """
        Infers a component type based on its name.
        """
        lname = name.lower()
        if "kpi" in lname:
            return "kpi"
        elif "metric" in lname:
            return "metric"
        elif "chart" in lname:
            return "chart"
        elif "table" in lname:
            return "table"
        elif "filter" in lname:
            return "filter"
        return "unknown"

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Runs the full cleaning pipeline.
        """
        df = self.normalize_column_names(df)
        df = self.convert_data_types(df)
        df = self.handle_missing_values(df)
        df = self.normalize_values(df)
        df = self.standardize_categories(df)
        df = self.parse_dates(df)
        return df

