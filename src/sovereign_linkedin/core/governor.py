"""
ModelNorth Sovereign LinkedIn Agent - Safety Governor & Rate Limiter
https://modelnorth.com

Strict enforcement of LinkedIn behavioral safety parameters:
- Prevents account shadowbans and rate-limit triggers.
- Enforces hard daily ceilings for connections, messages, and profile views.
- Halts automation during human curfew hours (late nights & off-peak).
- Records all operations to an immutable local ledger.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Optional
from sovereign_linkedin.config import SafetyLimits
from sovereign_linkedin.core.vault import SessionVault

logger = logging.getLogger("sovereign_linkedin.governor")


class SafetyCeilingError(Exception):
    """Raised when an operation would exceed safe LinkedIn rate limits."""
    pass


class SafetyGovernor:
    def __init__(self, limits: SafetyLimits, vault: SessionVault):
        self.limits = limits
        self.vault = vault

    def _get_today_key(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def check_active_hours(self) -> tuple[bool, str]:
        """Ensures operations only run during realistic human working hours."""
        current_hour = datetime.now().hour
        if not (self.limits.human_active_start_hour <= current_hour < self.limits.human_active_end_hour):
            return (
                False,
                f"Curfew active: Current local hour ({current_hour}:00) is outside allowed "
                f"window ({self.limits.human_active_start_hour}:00 - {self.limits.human_active_end_hour}:00)."
            )
        return True, "Within active working hours."

    def get_daily_metrics(self) -> dict[str, int]:
        ledger = self.vault.read_ledger()
        today = self._get_today_key()
        daily = ledger.get("daily_stats", {}).get(today, {})
        return {
            "invites_sent": daily.get("invites_sent", 0),
            "messages_sent": daily.get("messages_sent", 0),
            "profiles_viewed": daily.get("profiles_viewed", 0),
        }

    def can_send_invite(self) -> bool:
        metrics = self.get_daily_metrics()
        return metrics["invites_sent"] < self.limits.daily_connect_limit

    def can_send_message(self) -> bool:
        metrics = self.get_daily_metrics()
        return metrics["messages_sent"] < self.limits.daily_message_limit

    def can_view_profile(self) -> bool:
        metrics = self.get_daily_metrics()
        return metrics["profiles_viewed"] < self.limits.daily_profile_views

    def record_action(self, action_type: str, metadata: Optional[dict[str, Any]] = None) -> None:
        """Atomically record an action to the local sovereign vault ledger."""
        ledger = self.vault.read_ledger()
        today = self._get_today_key()

        if "daily_stats" not in ledger:
            ledger["daily_stats"] = {}
        if today not in ledger["daily_stats"]:
            ledger["daily_stats"][today] = {
                "invites_sent": 0,
                "messages_sent": 0,
                "profiles_viewed": 0
            }

        daily = ledger["daily_stats"][today]
        if action_type == "invite":
            daily["invites_sent"] = daily.get("invites_sent", 0) + 1
        elif action_type == "message":
            daily["messages_sent"] = daily.get("messages_sent", 0) + 1
        elif action_type == "view_profile":
            daily["profiles_viewed"] = daily.get("profiles_viewed", 0) + 1

        ledger["total_actions"] = ledger.get("total_actions", 0) + 1

        if metadata:
            if "lead_history" not in ledger:
                ledger["lead_history"] = []
            metadata["recorded_at"] = datetime.now(timezone.utc).isoformat()
            metadata["action"] = action_type
            ledger["lead_history"].append(metadata)
            # Keep history manageable
            if len(ledger["lead_history"]) > 1000:
                ledger["lead_history"] = ledger["lead_history"][-1000:]

        self.vault.write_ledger(ledger)
        logger.info(f"Recorded action '{action_type}' for {today}. Daily totals: {daily}")
