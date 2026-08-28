"""Parser for StevenBlack hosts file."""

async def parse(content: str) -> set[str]:
    """Parse StevenBlack hosts format and extract domains."""
    domains = set()
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Format is typically "0.0.0.0 domain.com" or "127.0.0.1 domain.com"
        parts = line.split()
        if len(parts) >= 2:
            ip = parts[0]
            domain = parts[1]
            if domain not in ("localhost", "localhost.localdomain", "broadcasthost", "local"):
                domains.add(domain)
    return domains
