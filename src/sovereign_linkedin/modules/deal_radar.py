"""
ModelNorth Sovereign LinkedIn Agent - Intent-Driven Deal Radar & Hiring Signal Sourcing
https://modelnorth.com

Hunts high-ticket enterprise deals ($5,000 - $30,000+) using active hiring intent signals:
1. Detects companies actively recruiting for AI Engineers, LLM Architects, and Heads of AI.
2. Correlates the hiring company to its executive decision-maker (CTO, VP Eng, Founder).
3. Synthesizes event-triggered "Hiring Gap 14-Day Sprint" outreach copy.
4. Manages the local deals pipeline ledger.
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Optional
import urllib.parse
from pydantic import BaseModel, Field

from sovereign_linkedin.core.telemetry import trace_agent_step
from sovereign_linkedin.modules.lead_scout import LeadScout

logger = logging.getLogger("sovereign_linkedin.deal_radar")


class HiringSignal(BaseModel):
    company_name: str
    job_title: str
    location: str
    job_url: str
    posted_days_ago: int = Field(default=3, description="Estimated days since job posting")
    tech_stack: list[str] = Field(default_factory=list)
    executive_name: Optional[str] = None
    executive_title: Optional[str] = None
    executive_url: Optional[str] = None
    intent_score: int = Field(default=85, description="0-100 Budget & Urgency Intent Score")
    discovered_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DealOpportunity(BaseModel):
    company: str
    decision_maker: str
    role_title: str
    hiring_gap_role: str
    location: str
    estimated_contract_value: str = "$10,000 - $25,000"
    stage: str = Field(default="DISCOVERED", description="DISCOVERED | CONTACTED | AUDIT_SENT | CALL_BOOKED | CLOSED")
    invite_note: str
    direct_message: str


class DealRadar:
    """Discovers high-intent enterprise buyers by tracking active hiring budgets."""

    HIGH_INTENT_TECH_TERMS = [
        "mcp", "model context protocol", "llm", "agents", "langchain",
        "langgraph", "voice ai", "rag", "fine-tuning", "on-prem",
        "air-gap", "deepseek", "data sovereignty", "security"
    ]

    @classmethod
    def calculate_intent_score(cls, job_title: str, tech_stack: list[str], days_ago: int) -> int:
        score = 70
        title_lower = job_title.lower()

        if any(term in title_lower for term in ["lead", "architect", "head", "director", "senior"]):
            score += 15
        if any(term in title_lower for term in ["agent", "llm", "mcp", "foundation"]):
            score += 10
        if days_ago <= 7:
            score += 5

        # Check tech stack richness
        matches = sum(1 for t in tech_stack if any(kw in t.lower() for kw in cls.HIGH_INTENT_TECH_TERMS))
        score += min(15, matches * 3)

        return min(100, score)

    @classmethod
    def build_job_search_url(cls, keywords: str, location: str) -> str:
        """Constructs an anti-ban LinkedIn job search endpoint."""
        query = urllib.parse.quote_plus(keywords)
        loc = urllib.parse.quote_plus(location)
        return f"https://www.linkedin.com/jobs/search/?keywords={query}&location={loc}&f_TPR=r604800&sortBy=DD"

    @classmethod
    def synthesize_hiring_gap_pitch(
        cls,
        executive_name: str,
        company: str,
        hiring_role: str,
        location: str = "Dubai"
    ) -> tuple[str, str]:
        """
        Generates peer-to-peer outreach offering an immediate 14-day production deployment sprint
        while their recruitment team screens candidates.
        """
        from sovereign_linkedin.modules.outreach import OutreachSynthesizer
        first_name = OutreachSynthesizer._extract_first_name(executive_name)

        # 1. Compliant connection note (< 300 chars)
        invite_note = (
            f"Hi {first_name}, noticed {company} is recruiting an {hiring_role} in {location}. "
            f"While your team interviews candidates, ModelNorth (modelnorth.com) deploys production on-prem "
            f"MCP servers & agent state machines in a 14-day sprint so delivery never stalls. Let's connect."
        )
        if len(invite_note) > 300:
            invite_note = invite_note[:297] + "..."

        # 2. Comprehensive direct message (post-acceptance)
        direct_message = (
            f"Hi {first_name},\n\n"
            f"Appreciate the connection. I saw {company} is actively searching for an {hiring_role}.\n\n"
            f"Recruiting senior AI infrastructure talent in the region typically takes 60 to 90 days. "
            f"In the interim, critical engineering roadmaps, internal tool integrations, and agent deployments "
            f"often stall waiting for onboarding.\n\n"
            f"At ModelNorth (modelnorth.com), we bridge that exact gap:\n"
            f"• We deploy hardened on-premise Model Context Protocol (MCP) servers in a 14-day architecture sprint.\n"
            f"• We configure air-gapped agent state machines with verified zero data egress.\n"
            f"• When your permanent hire joins, they step into a fully documented, defense-grade production codebase.\n\n"
            f"We're based in Dubai. If your leadership team is feeling the delivery pressure while recruiting, "
            f"happy to share a 1-page architecture brief or hop on a brief engineering sync.\n\n"
            f"Best regards,\n"
            f"ModelNorth Sovereign Engineering\n"
            f"https://modelnorth.com"
        )

        return invite_note, direct_message

    @classmethod
    async def scout_hiring_signals(
        cls,
        browser: Any,
        role_keyword: str = "AI Engineer",
        location: str = "Dubai, UAE",
        limit: int = 10
    ) -> list[HiringSignal]:
        """
        Scrapes live hiring signals from LinkedIn over CDP.
        Identifies enterprise companies actively allocating capital for AI talent.
        """
        with trace_agent_step("deal_radar.scout_hiring", action="hiring_search", role=role_keyword, location=location):
            search_url = cls.build_job_search_url(role_keyword, location)
            page = await browser.navigate_safely(search_url)

            # Wait for job listings container
            job_selectors = [
                "ul.jobs-search__results-list li",
                "div.job-card-container",
                "li[data-occludable-job-id]"
            ]

            signals: list[HiringSignal] = []
            cards = page.locator("div.job-card-container, li.jobs-search-results__list-item")
            count = await cards.count()

            for i in range(min(count, limit)):
                card = cards.nth(i)
                try:
                    title_el = card.locator("a.job-card-list__title, a.base-card__full-link").first
                    company_el = card.locator("span.job-card-container__primary-description, h4.base-search-card__subtitle").first
                    loc_el = card.locator("li.job-card-container__metadata-item, span.job-search-card__location").first

                    title = await title_el.inner_text() if await title_el.count() > 0 else role_keyword
                    company = await company_el.inner_text() if await company_el.count() > 0 else "Enterprise Prospect"
                    lead_loc = await loc_el.inner_text() if await loc_el.count() > 0 else location
                    job_link = await title_el.get_attribute("href") if await title_el.count() > 0 else search_url

                    signal = HiringSignal(
                        company_name=company.strip(),
                        job_title=title.strip(),
                        location=lead_loc.strip(),
                        job_url=job_link.split("?")[0] if job_link else "",
                        posted_days_ago=2,
                        tech_stack=["LLM", "Python", "MCP", "Agents"],
                        intent_score=cls.calculate_intent_score(title, ["LLM", "MCP"], 2)
                    )
                    signals.append(signal)
                except Exception as e:
                    logger.debug(f"Error parsing job card {i}: {e}")
                    continue

            return signals

    @classmethod
    def export_deals_pipeline(cls, deals: list[DealOpportunity], output_path: Path) -> Path:
        """Exports high-ticket opportunities to the local sovereign vault."""
        import csv
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Company",
                "Decision Maker",
                "Executive Role",
                "Hiring Need",
                "Location",
                "Estimated Value",
                "Pipeline Stage",
                "300-Char Invite Note",
                "Direct Message Pitch"
            ])
            for d in deals:
                writer.writerow([
                    d.company,
                    d.decision_maker,
                    d.role_title,
                    d.hiring_gap_role,
                    d.location,
                    d.estimated_contract_value,
                    d.stage,
                    d.invite_note,
                    d.direct_message
                ])
        logger.info(f"Exported {len(deals)} deal opportunities to: {output_path}")
        return output_path
