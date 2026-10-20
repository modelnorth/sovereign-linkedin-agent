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
