"""Parser for Feodo Tracker domain blocklist."""

async def parse(content: str) -> set[str]:
    """Parse Feodo Tracker blocklist and extract domains."""
    domains = set()
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Feodo domain blocklist has one domain per line
        domains.add(line)
    return domains
