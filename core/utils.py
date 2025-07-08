import csv
from django.conf import settings
from functools import lru_cache
from pathlib import Path
import pdfkit


@lru_cache(maxsize=None)
def get_us_states():
    """
    Load US states from CSV file and return them as a tuple of tuples.
    The result is cached using lru_cache to avoid reading the file multiple times.
    
    Returns:
        tuple: A tuple of tuples containing state codes and names, e.g. (('AL', 'Alabama'), ...)
    """
    try:
        csv_path = Path(settings.BASE_DIR) / 'data' / 'us_states.csv'
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            return tuple((row['code'], row['name']) for row in reader)
    except FileNotFoundError:
        # Return an empty tuple if the file is not found
        # This prevents the application from crashing        return tuple()


def render_pdf(html_string: str) -> bytes:
    """Render HTML content into a PDF using wkhtmltopdf via pdfkit.

    Args:
        html_string: The HTML content to convert.

    Returns:
        The generated PDF as bytes.
    """
    return pdfkit.from_string(html_string, False)
