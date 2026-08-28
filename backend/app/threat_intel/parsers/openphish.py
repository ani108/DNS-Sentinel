"""Parser for OpenPhish text feed."""
from urllib.parse import urlparse

async def parse(content: str) -> set[str]:
    """Parse OpenPhish feed and extract domains."""
    domains = set()
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            # Ensure it has a scheme to be parsed correctly
            if not line.startswith(('http://', 'https://')):
                line = 'http://' + line
            parsed = urlparse(line)
            if parsed.hostname:
                domains.add(parsed.hostname)
        except Exception:
            pass
    return domains
