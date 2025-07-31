from PIL import Image
from typing import Dict, Any, List
from paddleocr import PaddleOCR
import re
ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
def extract_text_from_kpi(cropped_image: Image.Image) -> Dict[str, Any]:
    """
    Extracts KPI information (label + value).
    """
    kpi_text = ocr.predict(cropped_image, cls=True)
    extracted_texts = [line[1][0] for line in kpi_text[0]] if kpi_text else []

    if not extracted_texts:
        return {"label": None, "value": None}

    # Look for numeric or percentage values
    value = next((t for t in extracted_texts if re.search(r'[\d,.%KMB]+', t)), None)
    label_candidates = [t for t in extracted_texts if t != value]

    return {
        "label": " ".join(label_candidates).strip() if label_candidates else None,
        "value": value
    }

def extract_table(cropped_image: Image.Image) -> Dict[str, Any]:
    """
    Extracts structured data from table images.
    """
    tabular_data = ocr.predict(cropped_image, cls=True)
    rows = [[line[1][0] for line in row_group] for row_group in tabular_data[0]] if tabular_data else []

    if not rows:
        return {"table": []}

    headers = rows[0]
    structured_table = []
    for row in rows[1:]:
        if len(row) == len(headers):
            structured_table.append(dict(zip(headers, row)))
        else:
            structured_table.append({"row_data": row})

    return {"table": structured_table}


def extract_chart_description(cropped_image: Image.Image) -> Dict[str, Any]:
    """
    Extracts chart metadata like title, axis labels, legend entries.

    Args:
        cropped_image (Image.Image): Cropped image of the chart.

    Returns:
        Dict[str, Any]: Metadata like {"title": "Sales Over Time", "x_axis": "Month", ...}
    """
    chart_text = ocr.predict(cropped_image, cls=True)
    chart_data = {
        "title": None,
        "x_axis": None,
        "y_axis": None,
        "legend": [],
        "other_text": []
    }
    title_candidates = []
    x_axis_candidates = []
    y_axis_candidates = []

    if chart_text:
        for line in chart_text[0]:
            text = line[1][0].strip()
            # Title detection: look for common title patterns or position (first line)
            if re.search(r'\b(title|chart|overview|summary)\b', text, re.IGNORECASE):
                title_candidates.append(text)
            # X-axis detection: look for axis keywords or common axis names
            elif re.search(r'\b(x[- ]?axis|horizontal|month|date|time|category|period)\b', text, re.IGNORECASE):
                x_axis_candidates.append(text)
            # Y-axis detection: look for axis keywords or common axis names
            elif re.search(r'\b(y[- ]?axis|vertical|value|amount|score|count|number|total)\b', text, re.IGNORECASE):
                y_axis_candidates.append(text)
            # Legend: look for legend keywords or typical legend entries
            elif re.search(r'\b(legend|series|group|class|type|category)\b', text, re.IGNORECASE):
                chart_data["legend"].append(text)
            else:
                chart_data["other_text"].append(text)

        # Assign best candidates
        chart_data["title"] = title_candidates[0] if title_candidates else (chart_text[0][0][1][0] if chart_text[0] else None)
        chart_data["x_axis"] = x_axis_candidates[0] if x_axis_candidates else None
        chart_data["y_axis"] = y_axis_candidates[0] if y_axis_candidates else None

        # If legend is empty, try to infer from other_text (e.g., if many short entries)
        if not chart_data["legend"]:
            possible_legends = [t for t in chart_data["other_text"] if len(t.split()) <= 3]
            chart_data["legend"] = possible_legends

    return chart_data

def extract_component_data(component: Dict, full_image: Image.Image) -> Dict[str, Any]:
    """
    Dispatches extraction based on component type.

    Args:
        component (Dict): Contains label, bbox, confidence.
        full_image (Image.Image): Original cleaned dashboard image.

    Returns:
        Dict[str, Any]: Extracted data + component metadata.
    """
    partial_image = full_image.crop(component['bbox'])
    confidence = component.get('confidence')
    if component['label'] == 'kpi':
        return {"type": "kpi", "data": extract_text_from_kpi(partial_image), "bbox": component['bbox'], "confidence": confidence}
    elif component['label'] == 'table':
        return {"type": "table", "data": extract_table(partial_image), "bbox": component['bbox'], "confidence": confidence}
    elif component['label'] in ['chart', 'title', 'legend', 'axis']:
        return {"type": "chart", "data": extract_chart_description(partial_image), "bbox": component['bbox'], "confidence": confidence}
    else:
        return {"type": "unknown", "data": {}, "bbox": component['bbox'], "confidence": confidence}