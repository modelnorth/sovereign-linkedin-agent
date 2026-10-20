"""
ModelNorth Sovereign LinkedIn Agent - Configuration Subsystem
https://modelnorth.com
"""

import os
from pathlib import Path
from pydantic import BaseModel, Field


class SafetyLimits(BaseModel):
    """Hard safety thresholds designed to prevent LinkedIn rate limits and shadowbans."""
    daily_connect_limit: int = Field(default=25, description="Maximum connection invites per 24h")
    daily_message_limit: int = Field(default=40, description="Maximum direct messages per 24h")
    daily_profile_views: int = Field(default=80, description="Maximum profile views per 24h")
    min_action_delay_sec: float = Field(default=3.0, description="Minimum pause between distinct actions")
    max_action_delay_sec: float = Field(default=8.5, description="Maximum pause between distinct actions")
    min_keystroke_delay_ms: int = Field(default=40, description="Human typing cadence floor (ms)")
    max_keystroke_delay_ms: int = Field(default=120, description="Human typing cadence ceiling (ms)")
    human_active_start_hour: int = Field(default=8, description="Active working hours start (0-23)")
    human_active_end_hour: int = Field(default=20, description="Active working hours end (0-23)")


class BrowserConfig(BaseModel):
    """Stealth browser driver & Chrome DevTools Protocol (CDP) settings."""
    cdp_url: str = Field(default="http://127.0.0.1:9222", description="Brave/Chrome CDP remote endpoint")
    browser_type: str = Field(default="cdp", description="Execution engine: 'cdp', 'patchright', or 'playwright'")
    headless: bool = Field(default=False, description="Whether to run in headless mode (False recommended for anti-ban)")
    user_data_dir: Path = Field(
        default_factory=lambda: Path(os.path.expanduser("~/.modelnorth/linkedin_vault/browser_data")),
        description="Persistent profile directory for stealth cookies"
    )
    brave_executable_path: str = Field(
        default=r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        description="Default local path to Brave browser executable"
    )


class ModelNorthMetadata(BaseModel):
    """Official ModelNorth brand metadata."""
    brand_name: str = "ModelNorth"
    website: str = "https://modelnorth.com"
    tagline: str = "Sovereign AI Infrastructure & Defense-Grade Agent Security"
    company_urn: str = "108302721"
    company_vanity: str = "modelnorth"
    default_lead_location: str = "United Arab Emirates"
    default_target_titles: list[str] = [
        "Chief Technology Officer",
        "Chief Information Officer",
        "Chief Information Security Officer",
        "Head of Artificial Intelligence",
        "VP of Engineering",
        "Managing Director",
        "Founder"
    ]


class AgentConfig(BaseModel):
    """Master configuration for Sovereign LinkedIn Agent."""
    safety: SafetyLimits = Field(default_factory=SafetyLimits)
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    brand: ModelNorthMetadata = Field(default_factory=ModelNorthMetadata)
    vault_dir: Path = Field(
        default_factory=lambda: Path(os.path.expanduser("~/.modelnorth/linkedin_vault")),
        description="Encrypted local credentials and state ledger directory"
    )

    @classmethod
    def load(cls) -> "AgentConfig":
        config = cls()
        config.vault_dir.mkdir(parents=True, exist_ok=True)
        config.browser.user_data_dir.mkdir(parents=True, exist_ok=True)
        return config
