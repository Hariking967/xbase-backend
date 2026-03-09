"""
Helper utilities for XBase Python execution environment.
Provides easy-to-use functions for data visualization and JSON output.
"""

import base64
from io import BytesIO
import json


def fig_to_base64(fig, format='png', dpi=150):
    """
    Convert a matplotlib figure to base64 string.
    
    Args:
        fig: matplotlib figure object
        format: image format (png, jpg, svg)
        dpi: dots per inch for raster formats
        
    Returns:
        dict with image_base64 and image_mime keys
    """
    import matplotlib.pyplot as plt
    
    buf = BytesIO()
    fig.savefig(buf, format=format, bbox_inches='tight', dpi=dpi)
    plt.close(fig)
    buf.seek(0)
    
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    mime_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'svg': 'image/svg+xml'
    }
    
    return {
        'image_base64': img_base64,
        'image_mime': mime_types.get(format, 'image/png')
    }


def create_visualization_result(fig, data=None, metrics=None, **kwargs):
    """
    Create a complete result object with visualization and data.
    
    Args:
        fig: matplotlib figure object
        data: optional data to include (list of dicts for tables)
        metrics: optional metrics dict (will be displayed as cards)
        **kwargs: any additional metadata
        
    Returns:
        dict ready to be set as 'result' variable
    """
    result = fig_to_base64(fig)
    
    if data is not None:
        result['data'] = data
    
    if metrics is not None:
        result['metrics'] = metrics
    
    # Add any additional fields
    result.update(kwargs)
    
    return result


def rows_to_csv(rows, fields=None):
    """
    Convert rows (list of tuples/lists) to CSV string.
    
    Args:
        rows: list of row data
        fields: optional list of field names for header
        
    Returns:
        CSV formatted string
    """
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    if fields:
        writer.writerow(fields)
    
    for row in rows:
        writer.writerow(row)
    
    return output.getvalue()


def format_table_result(rows, fields=None):
    """
    Format SQL-style rows into list of dicts for frontend table display.
    
    Args:
        rows: list of tuples or lists
        fields: list of column names
        
    Returns:
        list of dicts suitable for table rendering
    """
    if not fields or len(fields) != len(rows[0]):
        # Auto-generate field names
        fields = [f"col_{i}" for i in range(len(rows[0]))]
    
    return [dict(zip(fields, row)) for row in rows]


# Example usage templates for AI agent:
USAGE_EXAMPLES = """
# Example 1: Create a bar chart with data
import matplotlib.pyplot as plt
from helpers import create_visualization_result

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(data['x'], data['y'])
ax.set_title('Sales by Month')
ax.set_xlabel('Month')
ax.set_ylabel('Sales')

result = create_visualization_result(
    fig=fig,
    data=data_for_table,  # list of dicts
    metrics={'total_sales': 10000, 'avg_sale': 500}
)

# Example 2: Simple image-only result
import matplotlib.pyplot as plt
from helpers import fig_to_base64

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])
result = fig_to_base64(fig)

# Example 3: Convert SQL rows to table data
from helpers import format_table_result
result = {
    'data': format_table_result(rows, ['id', 'name', 'value'])
}
"""
