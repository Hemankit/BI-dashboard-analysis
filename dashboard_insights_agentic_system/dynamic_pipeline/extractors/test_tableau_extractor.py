import unittest
from unittest.mock import patch, MagicMock
from tableau_extractor import (
    extract_view_data,
    extract_filters_from_html,
    extract_filters_from_chart_series
)


class TestTableauExtractor(unittest.TestCase):

    @patch("tableau_extractor.requests.get")
    def test_extract_view_data_with_mocked_api(self, mock_get):
        # Mock API JSON response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"Name": "Alice", "Sales": 100},
                {"Name": "Bob", "Sales": 200}
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = extract_view_data(
            api_base_url="https://fake-tableau-server.com/api/3.8/sites/site-id",
            view_id="view-id",
            access_token="fake-token"
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["Name"], "Alice")
        mock_get.assert_called_once()

    def test_extract_filters_from_html(self):
        sample_html = """
        <html>
            <body>
                <div class="filter">
                    <label>Region</label>
                    <select>
                        <option>East</option>
                        <option>West</option>
                    </select>
                </div>
            </body>
        </html>
        """
        filters = extract_filters_from_html(sample_html)
        self.assertIn("Region", filters)
        self.assertEqual(filters["Region"], ["East", "West"])

    def test_extract_filters_from_chart_series(self):
        # Simulated chart data
        chart_data = [
            {"category": "Q1", "value": 100},
            {"category": "Q2", "value": 200}
        ]
        filters = extract_filters_from_chart_series(chart_data)
        self.assertIn("categories", filters)
        self.assertEqual(filters["categories"], ["Q1", "Q2"])


if __name__ == "__main__":
    unittest.main()