import pytest
from dashboard_insights_agentic_system.dynamic_pipeline.utils import ocr_helper

class DummyOCRHelper(ocr_helper.OCRHelper):
    def __init__(self):
        super().__init__()
        self.last_url = None
        self.last_img = None
    def extract_from_url(self, url):
        self.last_url = url
        return {"status": "success", "numbers": [1, 2, 3], "error": None}
    def extract_from_image(self, img):
        self.last_img = img
        return {"status": "success", "numbers": [4, 5], "error": None}

def test_extract_from_url_success():
    ocr = DummyOCRHelper()
    result = ocr.extract_from_url("http://example.com")
    assert result["status"] == "success"
    assert result["numbers"] == [1, 2, 3]
    assert ocr.last_url == "http://example.com"

def test_extract_from_image_success():
    ocr = DummyOCRHelper()
    result = ocr.extract_from_image("fake_image_data")
    assert result["status"] == "success"
    assert result["numbers"] == [4, 5]
    assert ocr.last_img == "fake_image_data"

def test_extract_from_url_error(monkeypatch):
    class FailingOCR(ocr_helper.OCRHelper):
        def extract_from_url(self, url):
            return {"status": "failed", "numbers": [], "error": "bad url"}
    ocr = FailingOCR()
    result = ocr.extract_from_url("bad_url")
    assert result["status"] == "failed"
    assert result["error"] == "bad url"

def test_extract_from_image_error(monkeypatch):
    class FailingOCR(ocr_helper.OCRHelper):
        def extract_from_image(self, img):
            return {"status": "failed", "numbers": [], "error": "bad img"}
    ocr = FailingOCR()
    result = ocr.extract_from_image("bad_img")
    assert result["status"] == "failed"
    assert result["error"] == "bad img"
