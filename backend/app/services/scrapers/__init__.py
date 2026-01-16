"""
Policy Update Scrapers

Monitors Fannie Mae and Freddie Mac for policy updates.
"""

from .fannie_mae_scraper import FannieMaeScraper
from .freddie_mac_scraper import FreddieMacScraper
from .base_scraper import BaseScraper

__all__ = [
    "BaseScraper",
    "FannieMaeScraper",
    "FreddieMacScraper",
]
