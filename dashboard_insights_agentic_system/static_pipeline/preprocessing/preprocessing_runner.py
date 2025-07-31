from PIL import Image

def preprocess_input(file_path: str) -> Image.Image:
    """
    Main entry point for preprocessing a dashboard input.

    Handles:
    - PDF → image conversion (if applicable)
    - Image cleanup and enhancement

    Args:
        file_path (str): Path to the input file (PDF or image).

    Returns:
        Image.Image: Preprocessed image suitable for downstream extraction.
        """
    try:
        # Attempt to convert PDF to image
        from dashboard_insights_agentic_system.static_pipeline.preprocessing.pdf_converter import convert_pdf_to_image
        image = convert_pdf_to_image(file_path)
    except AssertionError:
        # If not a PDF or conversion fails, assume it's an image file
        image = Image.open(file_path)

    # Clean and enhance the image
    from dashboard_insights_agentic_system.static_pipeline.preprocessing.image_cleaner import clean_image
    cleaned_image = clean_image(image)

    return cleaned_image