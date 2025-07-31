from pdf2image import convert_from_path

def convert_pdf_to_image(pdf_path: str):
    """
    Converts a single-page PDF into a PIL Image.

    Args:
        pdf_path (str): Path to the one-page PDF file.

    Returns:
        Image.Image: A PIL image object of the rendered PDF page.

    Raises:
        AssertionError: If the PDF contains more than one page.
    """
    images = convert_from_path(pdf_path)
    assert len(images) == 1, "PDF must contain exactly one page."
    return images[0]
    

    ### note: need to install poppler-utils for pdf2image to work ###