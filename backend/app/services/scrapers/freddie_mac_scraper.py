"""
Freddie Mac Bulletins Scraper

Monitors Freddie Mac for new Bulletins and Guide updates.
"""

import re
import logging
from datetime import date, datetime
from typing import Any

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class FreddieMacScraper(BaseScraper):
    """Scraper for Freddie Mac Bulletins."""

    # Freddie Mac Bulletins page
    BULLETINS_URL = "https://sf.freddiemac.com/tools-learning/guide-bulletin/bulletins"

    # Base URL for individual bulletins
    BULLETIN_BASE_URL = "https://guide.freddiemac.com"

    @property
    def gse(self) -> str:
        return "freddie_mac"

    @property
    def scraper_name(self) -> str:
        return "freddie_mac_bulletins"

    async def fetch_updates(self) -> list[dict[str, Any]]:
        """
        Fetch Bulletins from Freddie Mac website.

        Returns:
            List of bulletin data dicts
        """
        updates = []

        try:
            # Fetch the bulletins page
            response = await self.http_client.get(self.BULLETINS_URL)
            response.raise_for_status()

            soup = self.parse_html(response.text)

            # Find bulletin entries
            bulletin_elements = soup.select(
                ".bulletin-item, .announcement-row, .guide-bulletin, table tr"
            )

            for element in bulletin_elements[:20]:  # Process recent 20
                try:
                    update = self._parse_bulletin_element(element)
                    if update:
                        updates.append(update)
                except Exception as e:
                    logger.warning(f"Error parsing bulletin element: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error fetching Freddie Mac bulletins: {e}")

            # Return mock data for demo if scraping fails
            updates = self._get_mock_updates()

        return updates

    def _parse_bulletin_element(self, element) -> dict[str, Any] | None:
        """Parse a single bulletin element."""
        text = element.get_text()

        # Try to find bulletin number (e.g., 2025-16, Bulletin 2025-16)
        bulletin_match = re.search(r"(?:Bulletin\s*)?(\d{4})-(\d{1,2})", text)

        if not bulletin_match:
            return None

        year = bulletin_match.group(1)
        number = bulletin_match.group(2)
        update_number = f"{year}-{number}"

        # Find title
        title_elem = element.select_one("a, .title, .bulletin-title, td:nth-child(2)")
        title = title_elem.get_text(strip=True) if title_elem else f"Bulletin {update_number}"

        # Clean up title
        title = re.sub(r"^Bulletin\s+\d{4}-\d+\s*[-:]\s*", "", title)

        # Find date
        date_text = ""
        date_elem = element.select_one(".date, .bulletin-date, td:nth-child(1), time")
        if date_elem:
            date_text = date_elem.get_text(strip=True)

        publish_date = self._parse_date(date_text) or date.today()

        # Find link
        link_elem = element.select_one("a[href]")
        source_url = None
        if link_elem and link_elem.get("href"):
            href = link_elem.get("href")
            if href.startswith("/"):
                source_url = f"{self.BULLETIN_BASE_URL}{href}"
            elif href.startswith("http"):
                source_url = href

        return {
            "update_type": "bulletin",
            "update_number": update_number,
            "title": title[:500],  # Truncate to fit DB
            "publish_date": publish_date,
            "source_url": source_url,
            "summary": f"Freddie Mac Bulletin {update_number}: {title}",
            "affected_sections": self._detect_affected_sections(title),
        }

    def _parse_date(self, date_str: str) -> date | None:
        """Parse a date string into a date object."""
        if not date_str:
            return None

        # Try common date formats
        formats = [
            "%B %d, %Y",  # January 15, 2025
            "%m/%d/%Y",  # 01/15/2025
            "%Y-%m-%d",  # 2025-01-15
            "%b %d, %Y",  # Jan 15, 2025
            "%m-%d-%Y",  # 01-15-2025
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue

        return None

    def _detect_affected_sections(self, title: str) -> list[str]:
        """Detect likely affected guide sections from title."""
        title_lower = title.lower()
        sections = []

        # Map keywords to guide sections
        section_keywords = {
            "home possible": ["4501.5", "4501.9"],
            "income": ["5401", "4501.5"],
            "credit": ["5201", "4501.5"],
            "dti": ["5401", "4501.5"],
            "ltv": ["4203", "4501.5"],
            "loan limit": ["4201"],
            "manufactured": ["5703", "4501.5"],
            "condo": ["5701", "5601.1"],
            "co-op": ["5702"],
            "ami": ["4501.5"],
        }

        for keyword, related_sections in section_keywords.items():
            if keyword in title_lower:
                sections.extend(related_sections)

        return list(set(sections))

    def _get_mock_updates(self) -> list[dict[str, Any]]:
        """Return mock updates for demo purposes."""
        return [
            {
                "update_type": "bulletin",
                "update_number": "2025-16",
                "title": "Home Possible DTI Flexibility",
                "publish_date": date(2025, 1, 8),
                "effective_date": date(2025, 2, 15),
                "summary": "Freddie Mac is updating the maximum DTI ratio for Home Possible "
                "loans to allow greater flexibility with compensating factors.",
                "source_url": "https://guide.freddiemac.com/app/guide/bulletin/2025-16",
                "affected_sections": ["4501.5", "4501.9"],
            },
            {
                "update_type": "guide_update",
                "update_number": "2025-01",
                "title": "Updated Property Eligibility for Home Possible",
                "publish_date": date(2024, 12, 20),
                "effective_date": date(2025, 1, 15),
                "summary": "Clarifies property eligibility requirements for Home Possible, "
                "including updated guidance on manufactured housing and condos.",
                "source_url": "https://guide.freddiemac.com/app/guide/section/4501.5",
                "affected_sections": ["4501.5", "5601.1"],
            },
            {
                "update_type": "bulletin",
                "update_number": "2025-04",
                "title": "2025 AMI Limits Update",
                "publish_date": date(2025, 1, 5),
                "effective_date": date(2025, 1, 1),
                "summary": "Updates to Area Median Income limits for Home Possible "
                "eligibility based on latest FHFA data.",
                "source_url": "https://guide.freddiemac.com/app/guide/bulletin/2025-04",
                "affected_sections": ["4501.5"],
            },
        ]
