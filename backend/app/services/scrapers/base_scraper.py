"""
Base Scraper

Abstract base class for policy update scrapers.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import httpx
from bs4 import BeautifulSoup

from ...db import get_session, PolicyUpdate as DBPolicyUpdate, ScraperRun

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for GSE policy scrapers."""

    def __init__(self):
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; SAGE/1.0; +https://sage-app.fly.dev)"
            },
        )

    @property
    @abstractmethod
    def gse(self) -> str:
        """Return the GSE name (fannie_mae or freddie_mac)."""
        pass

    @property
    @abstractmethod
    def scraper_name(self) -> str:
        """Return the scraper name for logging."""
        pass

    @abstractmethod
    async def fetch_updates(self) -> list[dict[str, Any]]:
        """
        Fetch policy updates from the GSE website.

        Returns:
            List of dicts with update data
        """
        pass

    async def run(self) -> dict[str, Any]:
        """
        Run the scraper and save results to database.

        Returns:
            Summary of scraper run
        """
        run_id = None

        try:
            # Record scraper run start
            async with get_session() as session:
                scraper_run = ScraperRun(
                    scraper_name=self.scraper_name,
                    gse=self.gse,
                    status="running",
                )
                session.add(scraper_run)
                await session.flush()
                run_id = scraper_run.id

            logger.info(f"Starting {self.scraper_name} scraper")

            # Fetch updates
            updates = await self.fetch_updates()
            items_found = len(updates)
            items_new = 0

            # Save new updates to database
            async with get_session() as session:
                for update_data in updates:
                    # Check if update already exists
                    from sqlalchemy import select

                    result = await session.execute(
                        select(DBPolicyUpdate).where(
                            DBPolicyUpdate.update_number == update_data["update_number"]
                        )
                    )
                    existing = result.scalar_one_or_none()

                    if not existing:
                        # Create new update
                        db_update = DBPolicyUpdate(
                            gse=self.gse,
                            update_type=update_data.get("update_type", "guide_update"),
                            update_number=update_data["update_number"],
                            title=update_data["title"],
                            publish_date=update_data["publish_date"],
                            effective_date=update_data.get("effective_date"),
                            summary=update_data.get("summary", ""),
                            full_text=update_data.get("full_text"),
                            source_url=update_data.get("source_url"),
                            affected_sections=update_data.get("affected_sections", []),
                        )
                        session.add(db_update)
                        items_new += 1
                        logger.info(f"New update found: {update_data['update_number']}")

            # Update scraper run record
            async with get_session() as session:
                from sqlalchemy import update

                await session.execute(
                    update(ScraperRun)
                    .where(ScraperRun.id == run_id)
                    .values(
                        completed_at=datetime.utcnow(),
                        status="completed",
                        items_found=items_found,
                        items_new=items_new,
                    )
                )

            logger.info(
                f"{self.scraper_name} completed: {items_found} found, {items_new} new"
            )

            return {
                "scraper": self.scraper_name,
                "status": "completed",
                "items_found": items_found,
                "items_new": items_new,
            }

        except Exception as e:
            logger.error(f"{self.scraper_name} failed: {e}")

            # Update scraper run with error
            if run_id:
                async with get_session() as session:
                    from sqlalchemy import update

                    await session.execute(
                        update(ScraperRun)
                        .where(ScraperRun.id == run_id)
                        .values(
                            completed_at=datetime.utcnow(),
                            status="failed",
                            error_message=str(e),
                        )
                    )

            return {
                "scraper": self.scraper_name,
                "status": "failed",
                "error": str(e),
            }

    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content."""
        return BeautifulSoup(html, "lxml")
