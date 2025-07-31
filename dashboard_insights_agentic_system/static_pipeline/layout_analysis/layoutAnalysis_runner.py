
from PIL import Image
from typing import List, Dict
from .component_classifier import load_detection_model, detect_components
from .layout_detector import parse_layout
from .detection_visualization import draw_layout_boxes

def layout_processing_pipeline(image: Image.Image, model_path: str = None, save_path: str = None) -> Dict[str, List[Dict]]:
    """
    Processes the dashboard image to detect and classify layout components.

    Args:
        image (Image.Image): Input dashboard image.
        model_path (str): Optional path to a trained detection model.
        save_path (str): Optional path to save the annotated image.

    Returns:
        Dict[str, List[Dict]]: Structured layout components.
    """
    model = load_detection_model(model_path)
    detections = detect_components(image, model)
    layout = parse_layout(detections)
    
    if save_path:
        annotated_image = draw_layout_boxes(image, detections, save_path)
        annotated_image.show()  # Display the annotated image

    return layout