import unittest
from unittest.mock import MagicMock, patch

from crewai_tools.tools.brightdata_tool.brightdata_serp import BrightDataSearchTool


class TestBrightDataSearchTool(unittest.TestCase):
    @patch.dict(
        "os.environ",
        {"BRIGHT_DATA_API_KEY": "test_api_key", "BRIGHT_DATA_ZONE": "test_zone"},
    )
    def setUp(self):
        self.tool = BrightDataSearchTool()

    @patch("requests.post")
    def test_run_successful_search(self, mock_post):
        # Sample mock JSON response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "mock response text"
        mock_post.return_value = mock_response

        input_data = {
            "query": "latest AI news",
            "search_engine": "google",
            "country": "us",
            "language": "en",
            "search_type": "nws",
            "device_type": "desktop",
            "parse_results": True,
            "save_file": False,
        }

        result = self.tool._run(**input_data)

        self.assertEqual(result, "mock response text")
        mock_post.assert_called_once_with(
            self.tool.base_url,
            json={
                "zone": "test_zone",
                "url": "https://www.google.com/search?q=latest%20AI%20news"
                "&gl=us&hl=en&num=10&brd_json=1&tbm=nws",
                "format": "raw",
            },
            headers={
                "Authorization": "Bearer test_api_key",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

    @patch("requests.post")
    def test_run_with_request_exception(self, mock_post):
        mock_post.side_effect = Exception("Timeout")

        result = self.tool._run(query="AI", search_engine="google")
        self.assertIn("Error", result)

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
