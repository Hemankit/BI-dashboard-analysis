from PIL import Image
from typing import List, Dict, Any
from ultralytics import YOLO

# Optional: class names (should match training data)
CLASS_LABELS = ["chart", "table", "kpi", "title", "legend", "axis", "text"]

def load_detection_model(model_path: str = None) -> Any:
    """
    Loads the component detection model.

    Args:
        model_path (str): Optional path to a trained model.

    Returns:
        Any: Loaded model object.
    """
    trained_model_path = model_path or "dashboard_insights_agentic_system/static_pipeline/layout_analysis/component_detection_model.pt"
    try:
        model = YOLO(trained_model_path)
        return model
    except Exception as e:
        print(f"Error loading model from {trained_model_path}: {e}")
        return None 


def detect_components(image: Image.Image, model: Any) -> List[Dict]:
    """
    Detects layout components in the dashboard image.

    Args:
        image (Image.Image): Cleaned dashboard image.
        model (Any): Loaded component detection model.

    Returns:
        List[Dict]: List of detected components with bounding boxes and labels.
    """
    if not model:
        print("Model not loaded, cannot perform detection.")
        return []

    results = model(image)
    components = []

    for result in results:
        boxes = result.boxes
        for i in range(len(boxes)):
            box = boxes[i]
            class_idx = int(box.cls[0])
            label = CLASS_LABELS[class_idx] if class_idx < len(CLASS_LABELS) else f"class_{class_idx}"

            components.append({
                "label": label,
                "bbox": box.xyxy[0].tolist(),  # [x1, y1, x2, y2]
                "confidence": float(box.conf[0])
            })

    return components