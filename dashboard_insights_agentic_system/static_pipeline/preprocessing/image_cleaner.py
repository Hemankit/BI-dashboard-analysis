
from PIL import Image, ImageEnhance, ImageFilter

def resize_image(image: Image.Image, size: tuple = (1024, 768)) -> Image.Image:
    """
    Resizes the image to a fixed size using antialiasing (LANCZOS).

    Args:
        image (Image.Image): Input image.
        size (tuple): Desired output size (width, height).

    Returns:
        Image.Image: Resized image.
    """
    if image.size == size:
        return image
    if image.mode != 'RGB':
        image = image.convert('RGB')
    return image.resize(size, Image.Resampling.LANCZOS)

def enhance_contrast(image: Image.Image, factor: float = 1.2) -> Image.Image:
    """
    Enhances the contrast of an image.

    Args:
        image (Image.Image): Input image.
        factor (float): Contrast enhancement factor.

    Returns:
        Image.Image: Contrast-enhanced image.
    """
    contrast_enhancer = ImageEnhance.Contrast(image)
    return contrast_enhancer.enhance(factor)

def sharpen_image(image: Image.Image) -> Image.Image:
    """
    Sharpens the image using a default enhancement filter.

    Args:
        image (Image.Image): Input image.

    Returns:
        Image.Image: Sharpened image.
    """
    return image.filter(ImageFilter.SHARPEN)

def clean_image(image: Image.Image, size: tuple = (1024, 768), contrast_factor: float = 1.2) -> Image.Image:
    """
    Full image cleaning pipeline combining resizing, contrast enhancement, and sharpening.

    Color is preserved intentionally to retain semantic structure (e.g., legends, charts, KPIs).

    Args:
        image (Image.Image): Input image.
        size (tuple): Resize target.
        contrast_factor (float): Contrast enhancement factor.

    Returns:
        Image.Image: Cleaned image.
    """
    image = resize_image(image, size)
    image = enhance_contrast(image, contrast_factor)
    image = sharpen_image(image)
    return image

