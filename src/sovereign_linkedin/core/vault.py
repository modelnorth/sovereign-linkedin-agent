"""
ModelNorth Sovereign LinkedIn Agent - Local-First Session Vault
https://modelnorth.com

Enforces Zero-Trust credential security:
- Never asks for, sends, or logs your LinkedIn password.
- Attaches to your authentic local Brave or Chrome session over CDP.
- Stores local lead dossiers and session artifacts exclusively on your local disk.
"""

import json
import logging
import subprocess
import urllib.request
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("sovereign_linkedin.vault")


class SessionVault:
    def __init__(self, vault_dir: Path, cdp_url: str = "http://127.0.0.1:9222"):
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.cdp_url = cdp_url
        self.ledger_file = self.vault_dir / "activity_ledger.json"
        self._ensure_ledger()

    def _ensure_ledger(self) -> None:
        if not self.ledger_file.exists():
            initial_ledger = {
                "installed_at": "2026-10-20T00:00:00Z",
                "total_actions": 0,
                "daily_stats": {},
                "lead_history": []
            }
            self.ledger_file.write_text(json.dumps(initial_ledger, indent=2), encoding="utf-8")

    def read_ledger(self) -> dict[str, Any]:
        try:
            return json.loads(self.ledger_file.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"Failed to read ledger, returning default: {e}")
            return {"daily_stats": {}, "lead_history": []}

    def write_ledger(self, data: dict[str, Any]) -> None:
        self.ledger_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def check_cdp_status(self) -> bool:
        """Verify if local Brave/Chrome instance is running with remote debugging port active."""
        try:
            req = urllib.request.urlopen(f"{self.cdp_url}/json/version", timeout=2.5)
            data = json.loads(req.read().decode("utf-8"))
            return "Browser" in data or "webSocketDebuggerUrl" in data
        except Exception:
            return False

    def launch_brave_cdp(self, brave_path: str, port: int = 9222) -> bool:
        """Launch Brave browser in anti-ban debug mode with user profile detached."""
        if self.check_cdp_status():
            logger.info("CDP session already active.")
            return True

        if not Path(brave_path).exists():
            logger.error(f"Brave executable not found at: {brave_path}")
            return False

        profile_dir = self.vault_dir / "browser_profile"
        profile_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            brave_path,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={str(profile_dir)}",
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
            "https://www.linkedin.com"
        ]

        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Spawned Brave CDP instance on port {port}")
            return True
        except Exception as e:
            logger.error(f"Failed to launch Brave: {e}")
            return False

    def save_lead_dossier(self, lead_data: dict[str, Any]) -> Path:
        """Store prospect analysis permanently in the local sovereign vault."""
        dossier_dir = self.vault_dir / "leads"
        dossier_dir.mkdir(parents=True, exist_ok=True)
        slug = lead_data.get("public_id") or lead_data.get("name", "unknown").replace(" ", "_").lower()
        file_path = dossier_dir / f"{slug}.json"
        file_path.write_text(json.dumps(lead_data, indent=2), encoding="utf-8")
        return file_path
