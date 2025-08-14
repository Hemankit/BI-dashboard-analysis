import os
from unittest.mock import patch, MagicMock
from .PowerBI_extractor import (
    extract_table_data,
    extract_kpis,
    extract_filters_from_html,
    extract_filters_from_chart_series
)

# Toggle this flag for real vs. fake tests
USE_REAL = False

# Fake data for mocking
FAKE_API_BASE_URL = "https://fake.powerbi.api"
FAKE_DATASET_ID = "12345"
FAKE_TABLE_NAME = "SalesData"
FAKE_ACCESS_TOKEN = "fake_token"

FAKE_ROWS = {
    "value": [
        {"Date": "2025-01-01", "Sales": 100},
        {"Date": "2025-01-02", "Sales": 150}
    ]
}

FAKE_HTML = """
<html>
<body>
<table>
<thead><tr><th>Date</th><th>Sales</th></tr></thead>
<tbody>
<tr><td>2025-01-03</td><td>200</td></tr>
<tr><td>2025-01-04</td><td>250</td></tr>
</tbody>
</table>
</body>
</html>
"""

def test_extract_table_data_fake():
    if USE_REAL:
        print("Skipping fake test (running in real mode)")
        return

    with patch("powerbi_extractor.requests.get") as mock_get:
        # Mock API success
        mock_resp = MagicMock()
        mock_resp.json.return_value = FAKE_ROWS
        mock_resp.status_code = 200
        mock_resp.text = FAKE_HTML
        mock_get.return_value = mock_resp

        rows = extract_table_data(
            api_base_url=FAKE_API_BASE_URL,
            dataset_id=FAKE_DATASET_ID,
            table_name=FAKE_TABLE_NAME,
            access_token=FAKE_ACCESS_TOKEN
        )
        assert len(rows) == 2
        print("✅ Fake API test passed:", rows)


def test_extract_table_data_fallback_to_html():
    if USE_REAL:
        print("Skipping fake test (running in real mode)")
        return

    with patch("powerbi_extractor.requests.get") as mock_get:
        # Mock API failure to trigger HTML parsing
        mock_resp_fail = MagicMock()
        mock_resp_fail.json.return_value = {"value": []}
        mock_resp_fail.status_code = 200
        mock_resp_fail.text = FAKE_HTML
        mock_get.return_value = mock_resp_fail

        rows = extract_table_data(
            api_base_url=FAKE_API_BASE_URL,
            dataset_id=FAKE_DATASET_ID,
            table_name=FAKE_TABLE_NAME,
            access_token=FAKE_ACCESS_TOKEN
        )
        assert len(rows) == 2
        print("✅ HTML fallback test passed:", rows)


def test_extract_kpis_fake():
    if USE_REAL:
        print("Skipping fake test (running in real mode)")
        return

    with patch("powerbi_extractor.requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"value": [{"KPI": "Revenue", "Value": 5000}]}
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp

        kpis = extract_kpis(
            api_base_url=FAKE_API_BASE_URL,
            report_id="report123",
            access_token=FAKE_ACCESS_TOKEN
        )
        assert isinstance(kpis, list)
        print("✅ Fake KPI extraction test passed:", kpis)


def test_extract_filters_and_charts_fake():
    if USE_REAL:
        print("Skipping fake test (running in real mode)")
        return

    filters = extract_filters_from_html(FAKE_HTML)
    print("✅ Extracted filters (fake):", filters)

    chart_filters = extract_filters_from_chart_series(FAKE_HTML)
    print("✅ Extracted chart series filters (fake):", chart_filters)


if __name__ == "__main__":
    test_extract_table_data_fake()
    test_extract_table_data_fallback_to_html()
    test_extract_kpis_fake()
    test_extract_filters_and_charts_fake()

    if USE_REAL:
        # Example real run (fill in your real credentials here)
        real_api_base = os.getenv("POWERBI_API_BASE_URL")
        real_dataset_id = os.getenv("POWERBI_DATASET_ID")
        real_table_name = os.getenv("POWERBI_TABLE_NAME")
        real_token = os.getenv("POWERBI_ACCESS_TOKEN")

        rows = extract_table_data(
            api_base_url=real_api_base,
            dataset_id=real_dataset_id,
            table_name=real_table_name,
            access_token=real_token
        )
        print("Real API rows:", rows)
