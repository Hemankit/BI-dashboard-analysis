from PIL import Image, ImageDraw
from typing import List, Dict

def draw_layout_boxes(image: Image.Image, detections: List[Dict], save_path: str = None) -> Image.Image:
    """
    Draws bounding boxes around detected components.

    Args:
        image (Image.Image): Original image.
        detections (List[Dict]): Detection results.
        save_path (str): Optional path to save the annotated image.

    Returns:
        Image.Image: Image with boxes drawn.
    """
    image_draw = image.copy()
    draw = ImageDraw.Draw(image_draw)

    for item in detections:
        box = item["bbox"]
        label = item["label"]
        draw.rectangle(box, outline="red", width=2)
        draw.text((box[0], box[1] - 10), label, fill="red")

    if save_path:
        image_draw.save(save_path)

    return image_draw