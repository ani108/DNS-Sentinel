"""Parser for PhishTank JSON feed."""
import json
from urllib.parse import urlparse

async def parse(content: str) -> set[str]:
    """Parse PhishTank JSON and extract domains."""
    domains = set()
    try:
        data = json.loads(content)
        for entry in data:
            url = entry.get('url', '')
            if url:
                try:
                    parsed = urlparse(url)
                    if parsed.hostname:
                        domains.add(parsed.hostname)
                except Exception:
                    pass
    except json.JSONDecodeError:
        pass
    return domains
