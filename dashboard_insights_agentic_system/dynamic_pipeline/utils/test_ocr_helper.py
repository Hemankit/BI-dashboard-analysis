# test_ocr_helper.py

import os
from ocr_helper import extract_text_from_image, extract_text_from_url

# Test 1: Local image file
def test_local_image():
    test_image_path = "sample_dashboard_kpi.png"  # Replace with a valid image path
    if not os.path.exists(test_image_path):
        print(f"[SKIPPED] Local image file '{test_image_path}' not found.")
        return

    print("[TEST] Extracting text from local image...")
    text = extract_text_from_image(test_image_path)
    print("[RESULT - Local Image OCR]:")
    print(text if text.strip() else "[No text detected]")


# Test 2: Image from URL
def test_url_image():
    test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Tableau_Software_logo.svg/640px-Tableau_Software_logo.svg.png"
    print("[TEST] Extracting text from image URL...")
    text = extract_text_from_url(test_image_url)
    print("[RESULT - URL Image OCR]:")
    print(text if text.strip() else "[No text detected]")


if __name__ == "__main__":
    print("=== OCR Helper Test Suite ===\n")
    test_local_image()
    print("\n----------------------------\n")
    test_url_image()