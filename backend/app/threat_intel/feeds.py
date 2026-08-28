"""Threat intelligence feed configurations."""
from dataclasses import dataclass
from typing import Callable, Awaitable

@dataclass
class ThreatFeed:
    name: str
    url: str
    category: str
    parser_func: str  # Name of the function in the parsers module to use
    enabled: bool = True
