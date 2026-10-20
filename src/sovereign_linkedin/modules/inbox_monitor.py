"""
ModelNorth Sovereign LinkedIn Agent - Autonomous Inbox Sentinel
https://modelnorth.com

Monitors direct messages and company page inquiries:
- Triage and categorize incoming messages.
- Identifies high-value enterprise leads vs casual queries.
- Prepares contextual briefing dossiers for the executive team.
"""

import logging
from typing import Any
from pydantic import BaseModel, Field

logger = logging.getLogger("sovereign_linkedin.inbox")


class InboundMessage(BaseModel):
    sender_name: str
    sender_title: str = ""
    message_snippet: str
    received_at: str
    is_high_value: bool = False
    priority_level: str = Field(default="MEDIUM", description="LOW | MEDIUM | HIGH | URGENT")
    category: str = Field(default="INQUIRY", description="HIGH_TICKET_LEAD | ARCHITECTURE_QUESTION | SPAM | GENERAL")


class InboxMonitor:
    HIGH_INTENT_KEYWORDS = {
        "pricing", "quote", "pilot", "demo", "mcp", "sovereign", "enterprise",
        "contract", "call", "meeting", "deployment", "air-gap", "consulting",
        "partnership", "budget", "procurement", "rfp", "poc"
    }

    @classmethod
    def triage_message(cls, sender: str, title: str, text: str) -> InboundMessage:
        text_lower = text.lower()
        title_lower = title.lower()

        intent_hits = sum(1 for kw in cls.HIGH_INTENT_KEYWORDS if kw in text_lower)
        is_executive = any(exec_t in title_lower for exec_t in ["cto", "cio", "ciso", "founder", "head", "director", "vp"])

        is_high_val = intent_hits >= 2 or (intent_hits >= 1 and is_executive)

        priority = "LOW"
        category = "GENERAL"

        if is_high_val and is_executive:
            priority = "URGENT"
            category = "HIGH_TICKET_LEAD"
        elif is_high_val:
            priority = "HIGH"
            category = "HIGH_TICKET_LEAD"
        elif "question" in text_lower or "?" in text:
            category = "ARCHITECTURE_QUESTION"
            priority = "MEDIUM"

        return InboundMessage(
            sender_name=sender,
            sender_title=title,
            message_snippet=text,
            received_at="now",
            is_high_value=is_high_val,
            priority_level=priority,
            category=category
        )
