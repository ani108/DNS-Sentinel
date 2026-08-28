"""Parser for URLhaus CSV feed."""
import csv
import io
from urllib.parse import urlparse

async def parse(content: str) -> set[str]:
    """Parse URLhaus CSV and extract domains from URLs."""
    domains = set()
    reader = csv.reader(io.StringIO(content))
    for row in reader:
        # Ignore comments and empty rows
        if not row or row[0].startswith('#'):
            continue
        # URL is typically in the 3rd column (index 2)
        if len(row) > 2:
            url = row[2]
            try:
                parsed = urlparse(url)
                if parsed.hostname:
                    domains.add(parsed.hostname)
            except Exception:
                pass
    return domains
