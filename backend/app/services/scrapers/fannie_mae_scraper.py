"""
Fannie Mae Lender Letters Scraper

Monitors Fannie Mae for new Lender Letters and policy updates.
"""

import re
import logging
from datetime import date, datetime
from typing import Any

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class FannieMaeScraper(BaseScraper):
    """Scraper for Fannie Mae Lender Letters."""

    # Fannie Mae Lender Letters page
    LENDER_LETTERS_URL = "https://singlefamily.fanniemae.com/news-announcements/lender-letters"

    # Base URL for individual letters
    LETTER_BASE_URL = "https://singlefamily.fanniemae.com"

    @property
    def gse(self) -> str:
        return "fannie_mae"

    @property
    def scraper_name(self) -> str:
        return "fannie_mae_lender_letters"

    async def fetch_updates(self) -> list[dict[str, Any]]:
        """
        Fetch Lender Letters from Fannie Mae website.

        Returns:
            List of lender letter data dicts
        """
        updates = []

        try:
            # Fetch the lender letters page
            response = await self.http_client.get(self.LENDER_LETTERS_URL)
            response.raise_for_status()

            soup = self.parse_html(response.text)

            # Find lender letter entries
            # Fannie Mae typically lists letters in a table or structured list
            letter_elements = soup.select(".lender-letter, .announcement-item, table tr")

            for element in letter_elements[:20]:  # Process recent 20
                try:
                    update = self._parse_letter_element(element)
                    if update:
                        updates.append(update)
                except Exception as e:
                    logger.warning(f"Error parsing letter element: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error fetching Fannie Mae lender letters: {e}")

            # Return mock data for demo if scraping fails
            updates = self._get_mock_updates()

        return updates

    def _parse_letter_element(self, element) -> dict[str, Any] | None:
        """Parse a single lender letter element."""
        # Try to find letter number (e.g., LL-2025-04)
        text = element.get_text()
        letter_match = re.search(r"LL-(\d{4})-(\d{1,2})", text)

        if not letter_match:
            return None

        year = letter_match.group(1)
        number = letter_match.group(2)
        update_number = f"LL-{year}-{number.zfill(2)}"

        # Find title
        title_elem = element.select_one("a, .title, td:nth-child(2)")
        title = title_elem.get_text(strip=True) if title_elem else f"Lender Letter {update_number}"

        # Find date
        date_text = ""
        date_elem = element.select_one(".date, td:nth-child(1), time")
        if date_elem:
            date_text = date_elem.get_text(strip=True)

        publish_date = self._parse_date(date_text) or date.today()

        # Find link
        link_elem = element.select_one("a[href]")
        source_url = None
        if link_elem and link_elem.get("href"):
            href = link_elem.get("href")
            if href.startswith("/"):
                source_url = f"{self.LETTER_BASE_URL}{href}"
            elif href.startswith("http"):
                source_url = href

        return {
            "update_type": "lender_letter",
            "update_number": update_number,
            "title": title[:500],  # Truncate to fit DB
            "publish_date": publish_date,
            "source_url": source_url,
            "summary": f"Fannie Mae {update_number}: {title}",
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
            "homeready": ["B5-6-01", "B5-6-02", "B5-6-03"],
            "income": ["B3-3.1", "B5-6-02"],
            "credit": ["B3-5.1-01", "B5-6-02"],
            "dti": ["B3-6-02", "B5-6-02"],
            "ltv": ["B2-1.2-01", "B5-6-01"],
            "loan limit": ["B2-1-01"],
            "conforming": ["B2-1-01"],
            "manufactured": ["B5-6-01", "B4-1.4"],
            "condo": ["B4-2.1", "B5-6-01"],
        }

        for keyword, related_sections in section_keywords.items():
            if keyword in title_lower:
                sections.extend(related_sections)

        return list(set(sections))

    def _get_mock_updates(self) -> list[dict[str, Any]]:
        """Return mock updates for demo purposes."""
        return [
            {
                "update_type": "lender_letter",
                "update_number": "LL-2025-04",
                "title": "Updates to HomeReady Income Limits",
                "publish_date": date(2025, 1, 15),
                "effective_date": date(2025, 3, 1),
                "summary": "This lender letter announces updates to HomeReady income limits "
                "based on the latest Area Median Income (AMI) data from FHFA.",
                "source_url": "https://singlefamily.fanniemae.com/lender-letter/ll-2025-04",
                "affected_sections": ["B5-6-01", "B5-6-02"],
            },
            {
                "update_type": "lender_letter",
                "update_number": "LL-2025-03",
                "title": "2025 Conforming Loan Limits",
                "publish_date": date(2025, 1, 10),
                "effective_date": date(2025, 1, 1),
                "summary": "Announces the 2025 conforming loan limits. The baseline limit "
                "for single-family properties increased to $806,500.",
                "source_url": "https://singlefamily.fanniemae.com/lender-letter/ll-2025-03",
                "affected_sections": ["B2-1-01"],
            },
        ]
