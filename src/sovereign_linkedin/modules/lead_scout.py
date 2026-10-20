"""
ModelNorth Sovereign LinkedIn Agent - Lead Scout & Scoring Subsystem
https://modelnorth.com

Extracts, filters, and ranks high-ticket enterprise and government prospects.
Computes a Decision Authority Score (0-100) based on title seniority, industry,
and sovereignty relevance.
"""

import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("sovereign_linkedin.lead_scout")


class Prospect(BaseModel):
    name: str
    headline: str
    profile_url: str
    location: Optional[str] = None
    current_company: Optional[str] = None
    seniority_score: int = Field(default=50, description="0-100 Decision Authority Score")
    sovereign_fit_notes: list[str] = Field(default_factory=list)
    status: str = Field(default="discovered", description="discovered | contacted | connected | replied")
    discovered_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LeadScout:
    HIGH_VALUE_TITLES = {
        "cto": 95,
        "chief technology officer": 95,
        "ciso": 95,
        "chief information security officer": 95,
        "cio": 90,
        "chief information officer": 90,
        "founder": 90,
        "co-founder": 90,
        "head of ai": 88,
        "head of artificial intelligence": 88,
        "vp of engineering": 85,
        "vp engineering": 85,
        "director of engineering": 80,
        "managing director": 80,
        "enterprise architect": 75,
        "partner": 75,
    }

    GCC_KEYWORDS = {
        "dubai", "uae", "abu dhabi", "saudi", "riyadh", "qatar", "doha", "gcc",
        "emirates", "mena", "kuwait", "bahrain", "oman"
    }

    SOVEREIGN_TECH_KEYWORDS = {
        "sovereign", "defense", "security", "air-gap", "airgap", "on-prem",
        "governance", "data sovereignty", "compliance", "infrastructure", "ai agent",
        "mcp", "llm", "intelligence"
    }

    @classmethod
    def calculate_seniority_score(cls, headline: str, location: Optional[str] = None) -> tuple[int, list[str]]:
        score = 40
        notes = []
        hl_lower = headline.lower()

        # Title match
        for title, title_score in cls.HIGH_VALUE_TITLES.items():
            if title in hl_lower:
                if title_score > score:
                    score = title_score
                notes.append(f"Title seniority match: '{title}' (+{title_score})")
                break

        # Location boost (GCC sovereign focus)
        loc_str = (location or "").lower()
        if any(gcc_word in loc_str or gcc_word in hl_lower for gcc_word in cls.GCC_KEYWORDS):
            score = min(100, score + 10)
            notes.append("GCC / UAE regional relevance (+10)")

        # Sovereign tech alignment
        for tech in cls.SOVEREIGN_TECH_KEYWORDS:
            if tech in hl_lower:
                score = min(100, score + 5)
                notes.append(f"Sovereign domain synergy: '{tech}' (+5)")
                break

        return min(100, score), notes

    @classmethod
    def clean_name(cls, raw_name: str) -> str:
        """Strip badges, degrees (e.g. '• 2nd', '• 1st', 'Premium'), and whitespace."""
        text = raw_name.split("\n")[0].strip()
        for suffix in ["• 1st", "• 2nd", "• 3rd+", "• 3rd", "View ", "’s profile"]:
            text = text.replace(suffix, "")
        return text.strip()

    @classmethod
    def clean_url(cls, raw_url: str) -> str:
        """Strips tracking parameters from LinkedIn profile URLs."""
        if "?" in raw_url:
            return raw_url.split("?")[0]
        return raw_url

    @classmethod
    async def scrape_live_search(
        cls,
        browser: Any,
        keywords: str,
        location: Optional[str] = None,
        limit: int = 15,
        max_pages: int = 3
    ) -> list[Prospect]:
        """
        Executes live browser scraping of LinkedIn search results over CDP.
        Uses stealth human scrolling and anti-bot pauses to extract prospects.
        """
        import urllib.parse
        from sovereign_linkedin.core.stealth import StealthEngine

        query_parts = [keywords]
        if location:
            query_parts.append(location)
        search_query = " ".join(query_parts)
        encoded_query = urllib.parse.quote_plus(search_query)

        scraped_prospects: list[Prospect] = []
        seen_urls: set[str] = set()

        page = await browser.get_or_create_page()

        for page_num in range(1, max_pages + 1):
            if len(scraped_prospects) >= limit:
                break

            search_url = (
                f"https://www.linkedin.com/search/results/people/"
                f"?keywords={encoded_query}&page={page_num}&origin=GLOBAL_SEARCH_HEADER"
            )
            logger.info(f"Navigating to search page {page_num}: {search_url}")
            await browser.navigate_safely(search_url)

            # Wait for search results container
            result_selectors = [
                "li.reusable-search__result-container",
                "div.search-results-container",
                "div[data-chameleon-result-urn]",
                "div.entity-result"
            ]

            found_results = False
            for sel in result_selectors:
                if await page.locator(sel).count() > 0:
                    found_results = True
                    break

            if not found_results:
                logger.warning(f"No search result cards found on page {page_num}.")
                break

            # Natural human scroll to trigger lazy loading
            await StealthEngine.human_scroll(page, scroll_distance=900, steps=6)

            # Extract result cards
            cards = page.locator("li.reusable-search__result-container, div.entity-result")
            card_count = await cards.count()
            logger.info(f"Found {card_count} prospect cards on page {page_num}")

            for i in range(card_count):
                if len(scraped_prospects) >= limit:
                    break

                card = cards.nth(i)
                try:
                    # Extract profile link and name
                    link_el = card.locator("a.app-aware-link[href*='/in/']").first
                    if await link_el.count() == 0:
                        continue

                    raw_url = await link_el.get_attribute("href") or ""
                    url = cls.clean_url(raw_url)
                    if not url or url in seen_urls:
                        continue

                    raw_name = await link_el.inner_text()
                    name = cls.clean_name(raw_name)
                    if not name or "LinkedIn Member" in name:
                        continue

                    # Extract headline
                    hl_el = card.locator("div.entity-result__primary-subtitle, div[class*='subtitle']").first
                    headline = await hl_el.inner_text() if await hl_el.count() > 0 else ""
                    headline = headline.strip().replace("\n", " ")

                    # Extract location
                    loc_el = card.locator("div.entity-result__secondary-subtitle, div[class*='secondary-subtitle']").first
                    lead_loc = await loc_el.inner_text() if await loc_el.count() > 0 else location

                    # Compute score and notes
                    score, notes = cls.calculate_seniority_score(headline, lead_loc)

                    prospect = Prospect(
                        name=name,
                        headline=headline,
                        profile_url=url,
                        location=lead_loc,
                        seniority_score=score,
                        sovereign_fit_notes=notes
                    )

                    seen_urls.add(url)
                    scraped_prospects.append(prospect)
                    logger.info(f"Scraped lead: {name} ({headline}) | Score: {score}")

                except Exception as e:
                    logger.debug(f"Error parsing card {i}: {e}")
                    continue

        return scraped_prospects

    @classmethod
    def parse_raw_profile(cls, raw: dict[str, Any]) -> Prospect:
        name = raw.get("name") or raw.get("title", "Unknown Prospect")
        headline = raw.get("headline") or raw.get("subtitle", "")
        url = raw.get("profile_url") or raw.get("link", "")
        location = raw.get("location")
        company = raw.get("company")

        score, notes = cls.calculate_seniority_score(headline, location)
        return Prospect(
            name=name,
            headline=headline,
            profile_url=url,
            location=location,
            current_company=company,
            seniority_score=score,
            sovereign_fit_notes=notes
        )

    @classmethod
    def export_csv(cls, prospects: list[Prospect], output_path: Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Name",
                "Seniority Score",
                "Headline",
                "Current Company",
                "Location",
                "Profile URL",
                "Fit Notes",
                "Status",
                "Discovered At"
            ])
            for p in prospects:
                writer.writerow([
                    p.name,
                    p.seniority_score,
                    p.headline,
                    p.current_company or "",
                    p.location or "",
                    p.profile_url,
                    "; ".join(p.sovereign_fit_notes),
                    p.status,
                    p.discovered_at
                ])
        logger.info(f"Exported {len(prospects)} leads to CSV at: {output_path}")
        return output_path

    @classmethod
    def export_json(cls, prospects: list[Prospect], output_path: Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = [p.model_dump() for p in prospects]
        output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        logger.info(f"Exported {len(prospects)} leads to JSON at: {output_path}")
        return output_path
