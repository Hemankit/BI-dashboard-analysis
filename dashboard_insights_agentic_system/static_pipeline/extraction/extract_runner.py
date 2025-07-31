from PIL import Image
from typing import Dict, Any
from dashboard_insights_agentic_system.static_pipeline.extraction.extractor import (
    extract_text_from_kpi,
    extract_table,
    extract_chart_description
)



def extract_all_dashboard_components(
    full_image: Image.Image, components: list[Dict[str, Any]]
) -> list[Dict[str, Any]]:
    """
    Extracts structured data from all detected dashboard components.

    Args:
        full_image (Image.Image): Full dashboard image.
        components (list[Dict[str, Any]]): List of detected components with bounding boxes.

    Returns:
        list[Dict[str, Any]]: List of extracted data + component metadata.
    """
    extracted_data = []
    
    for component in components:
        partial_image = full_image.crop(component['bbox'])
        confidence = component.get('confidence')
        
        if component['label'] == 'kpi':
            extracted_data.append({
                "type": "kpi",
                "data": extract_text_from_kpi(partial_image),
                "bbox": component['bbox'],
                "confidence": confidence
            })
        elif component['label'] == 'table':
            extracted_data.append({
                "type": "table",
                "data": extract_table(partial_image),
                "bbox": component['bbox'],
                "confidence": confidence
            })
        elif component['label'] in ['chart', 'title', 'legend', 'axis']:
            extracted_data.append({
                "type": "chart",
                "data": extract_chart_description(partial_image),
                "bbox": component['bbox'],
                "confidence": confidence
            })
        else:
            extracted_data.append({
                "type": "unknown",
                "data": {},
                "bbox": component['bbox'],
                "confidence": confidence
            })

    return extracted_data