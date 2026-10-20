"""
ModelNorth Sovereign LinkedIn Agent - Contextual Outreach Synthesizer
https://modelnorth.com

Synthesizes high-status, non-salesy outreach messages for enterprise & government leaders:
- Strict character limits (300 chars for invite notes, 1000 chars for direct InMail).
- High-status peer-to-peer positioning (Zero AI hype, defense-grade technical depth).
- Three bespoke tactical angles: Sovereign Architecture, MCP Security, and Air-Gapped AI.
"""

from typing import Optional
from sovereign_linkedin.modules.lead_scout import Prospect


class OutreachSynthesizer:
    """Generates precision outreach copy tailored to prospect data."""

    @staticmethod
    def _extract_first_name(full_name: str) -> str:
        parts = full_name.strip().split()
        if not parts:
            return "there"
        first = parts[0]
        # Clean titles
        if first.lower() in {"dr.", "eng.", "mr.", "ms.", "sheikh", "h.e."} and len(parts) > 1:
            return parts[1]
        return first

    @classmethod
    def synthesize_invite_note(cls, prospect: Prospect, angle: str = "sovereign") -> str:
        """
        Generates connection invite note strictly under LinkedIn's 300-character cap.
        Angles: 'sovereign' | 'mcp_security' | 'enterprise_ai'
        """
        first_name = cls._extract_first_name(prospect.name)
        company = prospect.current_company or "your team"

        if angle == "mcp_security":
            note = (
                f"Hi {first_name}, noticed your engineering focus at {company}. "
                f"We're developing defense-grade MCP security protocols & air-gapped agent runtime "
                f"at ModelNorth (modelnorth.com). Would value connecting with fellow architects in the region."
            )
        elif angle == "enterprise_ai":
            note = (
                f"Hi {first_name}, following your work leading tech at {company}. "
                f"We build deterministic on-prem agent infrastructure for GCC enterprise at ModelNorth (Dubai). "
                f"Would love to connect and share notes on sovereign AI deployments."
            )
        else:  # default 'sovereign'
            note = (
                f"Hi {first_name}, noticed your leadership at {company}. "
                f"At ModelNorth (modelnorth.com), we architect sovereign, air-gapped agent infrastructure "
                f"for GCC enterprise and defense. Would value having you in my network."
            )

        # Enforce hard 300-char LinkedIn constraint
        if len(note) > 300:
            note = note[:297] + "..."
        return note

    @classmethod
    def synthesize_direct_message(
        cls,
        prospect: Prospect,
        custom_pain_point: Optional[str] = None
    ) -> str:
        """
        Generates comprehensive direct message / InMail for accepted connections.
        Positions ModelNorth as sovereign technical peer.
        """
        first_name = cls._extract_first_name(prospect.name)
        company = prospect.current_company or "your organization"

        pain_context = (
            custom_pain_point
            or "transitioning from fragile prototype wrappers to deterministic, sovereign enterprise agents"
        )

        message = (
            f"Hi {first_name},\n\n"
            f"Appreciate the connection. I've been tracking technical initiatives at {company}.\n\n"
            f"Most enterprise engineering teams we speak with in the GCC are currently solving {pain_context}—specifically "
            f"preventing sensitive data egress to public cloud APIs and eliminating nondeterministic agent loops.\n\n"
            f"At ModelNorth (modelnorth.com), we architect:\n"
            f"• Air-gapped on-premise foundation model deployment with verified UAE/Saudi data residency.\n"
            f"• Hardened Model Context Protocol (MCP) servers with zero-trust RBAC and perimeter defense.\n"
            f"• Deterministic multi-agent state machines with sub-second execution latency.\n\n"
            f"If your team is evaluating sovereign infrastructure or running security audits on autonomous pipelines, "
            f"happy to share an architectural brief or hop on a brief engineering sync.\n\n"
            f"Best regards,\n"
            f"ModelNorth Sovereign Engineering\n"
            f"https://modelnorth.com"
        )
        return message
