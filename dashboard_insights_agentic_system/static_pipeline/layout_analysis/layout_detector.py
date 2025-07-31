from typing import List, Dict

def parse_layout(detections: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Parses raw detection output into structured layout components.

    Args:
        detections (List[Dict]): List of raw detection outputs.

    Returns:
        Dict[str, List[Dict]]: Structured layout dictionary.
        Example:
        {
            "charts": [{"bbox": [...], "confidence": 0.92}],
            "tables": [{"bbox": [...], "confidence": 0.89}],
            "titles": [{"bbox": [...], "confidence": 0.95}]
        }
    """
    parsed = {}
    for item in detections:
        label = item['label']
        parsed.setdefault(label + 's', []).append({
            "bbox": item["bbox"],
            "confidence": item.get("confidence", 1.0)
        })
    return parsed