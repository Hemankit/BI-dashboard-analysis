import plotly.graph_objs as go
import plotly.io as pio
from typing import Dict, Any, Optional, List
import matplotlib.pyplot as plt
import io
import base64
import matplotlib.patches as mpatches
from matplotlib.table import Table
import numpy as np
import requests


def render_dashboard(dashboard_data: Dict[str, Any]) -> str:
    """
    Render the dashboard using the provided unified schema data.

    Args:
        dashboard_data: The dashboard dict in unified schema.

    Returns:
        A base64-encoded string of the rendered dashboard image.
    """

    # Set up figure
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    y = 1.0
    line_height = 0.05

    def draw_text(text, fontsize=12, color='black', weight='normal'):
        nonlocal y
        ax.text(0, y, text, fontsize=fontsize, color=color, weight=weight, va='top', ha='left', wrap=True)
        y -= line_height

    # Title
    draw_text(f"Dashboard Source: {dashboard_data.get('source', '')} | Auth: {dashboard_data.get('auth_type', '')}", 16, 'navy', 'bold')
    draw_text(f"Status: {dashboard_data.get('status', '')}", 12, 'green' if dashboard_data.get('status')=='success' else 'red', 'bold')
    if dashboard_data.get('error'):
        draw_text(f"Error: {dashboard_data['error']}", 12, 'red')

    # Drill state
    if dashboard_data.get('drill_state'):
        draw_text(f"Drill State: {dashboard_data['drill_state']}", 10, 'purple')

    # KPIs
    kpis = dashboard_data.get('kpis', [])
    if kpis:
        draw_text("KPIs:", 14, 'darkblue', 'bold')
        for kpi in kpis:
            if isinstance(kpi, dict):
                kpi_str = f"{kpi.get('name', '')}: {kpi.get('value', '')}"
            else:
                kpi_str = str(kpi)
            draw_text(f"  {kpi_str}", 12, 'black')

    # Tables
    tables = dashboard_data.get('tables', [])
    if tables:
        draw_text("Tables:", 14, 'darkblue', 'bold')
        for idx, table in enumerate(tables):
            headers = table.get('headers', [])
            rows = table.get('rows', [])
            if headers and rows:
                # Draw as matplotlib table
                y_table = y
                tab = Table(ax, bbox=[0, y_table-0.15, 0.8, 0.12])
                for col, header in enumerate(headers):
                    tab.add_cell(0, col, 0.1, 0.03, text=header, loc='center', facecolor='#cccccc')
                for row_idx, row in enumerate(rows):
                    for col, cell in enumerate(row):
                        tab.add_cell(row_idx+1, col, 0.1, 0.03, text=str(cell), loc='center', facecolor='#f9f9f9')
                ax.add_table(tab)
                y -= 0.15
            else:
                draw_text(f"  Table {idx+1}: {table}", 10)

    # Filters
    filters = dashboard_data.get('filters', [])
    if filters:
        draw_text("Filters:", 14, 'darkblue', 'bold')
        for f in filters:
            draw_text(f"  {f}", 10, 'gray')

    # Visuals (images, SVGs)
    visuals = dashboard_data.get('visuals', [])
    if visuals:
        draw_text("Visuals:", 14, 'darkblue', 'bold')
        for v in visuals:
            if isinstance(v, dict) and v.get('type') == 'image' and v.get('src'):
                try:
                    # Try to load and plot the image inline (if it's a URL)
                    import requests
                    from PIL import Image
                    from io import BytesIO
                    response = requests.get(v['src'], timeout=2)
                    img = Image.open(BytesIO(response.content))
                    ax_img = fig.add_axes([0.7, y-0.1, 0.25, 0.15])
                    ax_img.imshow(img)
                    ax_img.axis('off')
                    y -= 0.18
                except Exception:
                    draw_text(f"  [Image: {v.get('alt', v.get('src', ''))}]", 10, 'gray')
            elif isinstance(v, dict) and v.get('type') == 'svg':
                draw_text(f"  [SVG visual]", 10, 'gray')
            else:
                draw_text(f"  {v}", 10, 'gray')

    # Layout
    layout = dashboard_data.get('layout', {})
    if layout:
        draw_text("Layout:", 14, 'darkblue', 'bold')
        draw_text(f"  {layout}", 10, 'gray')

    # Components (with highlights)
    components = dashboard_data.get('components', [])
    if components:
        draw_text("Components:", 14, 'darkblue', 'bold')
        for comp in components:
            ctype = comp.get('type', 'component')
            highlights = comp.get('highlights', [])
            summary = f"  {ctype.title()}: " + ", ".join(f"{k}={v}" for k, v in comp.items() if k != 'highlights')
            draw_text(summary, 10, 'black')
            if highlights:
                draw_text(f"    Highlights: {highlights}", 10, 'orange')

    # HTML text (if present)
    html_text = dashboard_data.get('html_text', '')
    if html_text:
        draw_text("HTML Text (excerpt):", 12, 'darkblue', 'bold')
        draw_text(html_text[:200] + ("..." if len(html_text) > 200 else ""), 8, 'gray')

    # Save the figure to a BytesIO object
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)

    # Encode the image to base64
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{img_base64}"