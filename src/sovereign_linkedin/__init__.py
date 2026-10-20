"""
Sovereign LinkedIn Agent by ModelNorth
https://modelnorth.com

Autonomous, Anti-Ban LinkedIn Intelligence & Sovereign Growth Engine.
Equipped with dual MCP + Stealth CDP browser execution, deep lead extraction,
contextual outreach synthesis, and air-gapped zero-trust security.
"""

__version__ = "1.0.0"
__author__ = "ModelNorth Sovereign AI"
__email__ = "engineering@modelnorth.com"
__homepage__ = "https://modelnorth.com"
__license__ = "ModelNorth Sovereign Open License (MN-SL v1.0)"

from sovereign_linkedin.config import AgentConfig
from sovereign_linkedin.core.stealth import StealthEngine
from sovereign_linkedin.core.governor import SafetyGovernor
from sovereign_linkedin.core.vault import SessionVault
from sovereign_linkedin.modules.lead_scout import LeadScout
from sovereign_linkedin.modules.outreach import OutreachSynthesizer

__all__ = [
    "AgentConfig",
    "StealthEngine",
    "SafetyGovernor",
    "SessionVault",
    "LeadScout",
    "OutreachSynthesizer",
]
