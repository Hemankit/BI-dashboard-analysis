# ocr_helper.py
import io
import re
import logging
from typing import Optional, Union, Dict, Any, List
from urllib.parse import urlparse

import pytesseract
import requests
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

logger = logging.getLogger(__name__)


class OCRHelper:
    """
    Utility class for performing OCR on images (files, bytes, PIL Image, or URLs).
    Returns structured results with extracted text and numbers.
    """

    def __init__(self, tesseract_cmd: Optional[str] = None, session: Optional[requests.Session] = None):
        """
        :param tesseract_cmd: Optional path to the tesseract executable (if not in PATH).
        :param session: Optional requests.Session for URL downloads (reused for performance).
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self.session = session or requests.Session()

    def _preprocess_image(self, image: Image.Image, binarize: bool = True) -> Image.Image:
        """
        Enhance the image for better OCR accuracy.
        """
        # Convert to grayscale
        image = image.convert("L")

        # Optional binarization (thresholding)
        if binarize:
            image = ImageOps.autocontrast(image)
            image = image.point(lambda x: 0 if x < 140 else 255, '1')

        # Increase contrast
        image = ImageEnhance.Contrast(image).enhance(2)

        # Sharpen image
        image = image.filter(ImageFilter.SHARPEN)

        return image

    def _load_image(self, image_input: Union[str, bytes, Image.Image]) -> Image.Image:
        """
        Load image from path, bytes, URL, or PIL.Image.
        """
        if isinstance(image_input, str):
            if urlparse(image_input).scheme in ("http", "https"):
                return self._load_from_url(image_input)
            return Image.open(image_input)
        elif isinstance(image_input, bytes):
            return Image.open(io.BytesIO(image_input))
        elif isinstance(image_input, Image.Image):
            return image_input
        else:
            raise ValueError(f"Unsupported image_input type: {type(image_input)}")

    def _load_from_url(self, url: str) -> Image.Image:
        """
        Fetch an image from a URL.
        """
        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            return Image.open(io.BytesIO(resp.content))
        except Exception as e:
            logger.exception(f"Failed to download image from URL: {url}")
            raise

    def extract_text(self, image_input: Union[str, bytes, Image.Image], lang: str = "eng", binarize: bool = True) -> str:
        """
        Perform OCR and return extracted text.
        """
        image = self._load_image(image_input)
        image = self._preprocess_image(image, binarize=binarize)
        return pytesseract.image_to_string(image, lang=lang).strip()

    def extract_numbers(self, image_input: Union[str, bytes, Image.Image], lang: str = "eng", binarize: bool = True) -> List[float]:
        """
        Perform OCR and extract all numbers from the text.
        """
        text = self.extract_text(image_input, lang=lang, binarize=binarize)
        numbers = re.findall(r"[-+]?\d[\d,]*\.?\d*", text)
        return [float(num.replace(",", "")) for num in numbers] if numbers else []

    def extract_structured(self, image_input: Union[str, bytes, Image.Image], lang: str = "eng", binarize: bool = True) -> Dict[str, Any]:
        """
        Perform OCR and return structured results with text and numbers.
        """
        try:
            text = self.extract_text(image_input, lang=lang, binarize=binarize)
            numbers = re.findall(r"[-+]?\d[\d,]*\.?\d*", text)
            return {
                "status": "success",
                "text": text,
                "numbers": [float(num.replace(",", "")) for num in numbers],
                "error": None
            }
        except Exception as e:
            logger.exception("OCR extraction failed.")
            return {"status": "failed", "text": "", "numbers": [], "error": str(e)}

    def extract_from_url(self, url: str, lang: str = "eng", binarize: bool = True) -> Dict[str, Any]:
        """
        Shortcut for extracting OCR results directly from an image URL.
        """
        try:
            image = self._load_from_url(url)
            return self.extract_structured(image, lang=lang, binarize=binarize)
        except Exception as e:
            return {"status": "failed", "text": "", "numbers": [], "error": str(e)}