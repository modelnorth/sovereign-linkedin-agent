"""
ModelNorth Sovereign LinkedIn Agent - Autonomous Content Scheduler & Queue Manager
https://modelnorth.com

Handles automated publishing workflows with OpenTelemetry tracing:
- Manages local posts queue and content calendar.
- Locates next scheduled or pending high-impact post.
- Dispatches post via Stealth CDP browser engine.
- Tracks execution telemetry, latencies, and confirmation proof.
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field

from sovereign_linkedin.config import AgentConfig
from sovereign_linkedin.core.telemetry import trace_agent_step
from sovereign_linkedin.core.governor import SafetyGovernor
from sovereign_linkedin.core.vault import SessionVault
from sovereign_linkedin.engine.browser import BrowserDriver
from sovereign_linkedin.modules.company_page import CompanyPagePilot

logger = logging.getLogger("sovereign_linkedin.scheduler")


class QueuedPost(BaseModel):
    id: int
    title: str
    status: str = Field(default="queued", description="queued | published | draft")
    image_path: Optional[str] = None
    content: str
    published_at: Optional[str] = None


class ContentScheduler:
    DEFAULT_QUEUE_PATH = Path(r"C:\Users\DELL\Desktop\ModelNorth_LinkedIn_Assets\4_LinkedIn_Content_Calendar_5_Posts.json")

    def __init__(self, config: AgentConfig, queue_path: Optional[Path] = None):
        self.config = config
        self.queue_path = Path(queue_path or self.DEFAULT_QUEUE_PATH)
        self.vault = SessionVault(config.vault_dir, config.browser.cdp_url)
        self.governor = SafetyGovernor(config.safety, self.vault)

    def load_queue(self) -> list[QueuedPost]:
        """Loads all posts from the content calendar queue."""
        if not self.queue_path.exists():
            logger.warning(f"Queue file not found at: {self.queue_path}")
            return []
        try:
            raw_data = json.loads(self.queue_path.read_text(encoding="utf-8"))
            return [QueuedPost(**item) for item in raw_data]
        except Exception as e:
            logger.error(f"Error loading posts queue: {e}")
            return []

    def save_queue(self, posts: list[QueuedPost]) -> None:
        """Saves updated posts state back to the queue file."""
        data = [p.model_dump() for p in posts]
        self.queue_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def get_next_pending_post(self) -> Optional[QueuedPost]:
        """Retrieves the earliest queued post that has not been published yet."""
        posts = self.load_queue()
        for p in posts:
            if p.status.lower() == "queued":
                return p
        return None

    async def publish_next(self, force: bool = False) -> tuple[bool, str, Optional[QueuedPost]]:
        """
        Executes autonomous publishing of the next queued post with full OpenTelemetry tracing.
        """
        trace_attrs = {
            "queue_file": str(self.queue_path),
            "force_flag": force
        }

        with trace_agent_step("scheduler.publish_next", action="publish_post", **trace_attrs) as span:
            # 1. Governor check
            within_hours, msg = self.governor.check_active_hours()
            if not within_hours and not force:
                logger.warning(f"Publishing blocked by Safety Governor: {msg}")
                return False, f"Curfew blocked: {msg}", None

            # 2. Get next post
            post = self.get_next_pending_post()
            if not post:
                return False, "Queue is empty. No posts with status='queued' found.", None

            logger.info(f"Targeting Post #{post.id}: '{post.title}'")

            # 3. Connect browser and publish
            browser = BrowserDriver(self.config)
            pilot = CompanyPagePilot(self.config, browser)

            try:
                with trace_agent_step(
                    "browser.cdp_publish",
                    action="browser_automation",
                    post_id=post.id,
                    title=post.title
                ):
                    media_file = Path(post.image_path) if post.image_path and Path(post.image_path).exists() else None
                    success = await pilot.publish_company_post(
                        post_text=post.content,
                        media_path=media_file
                    )

                if success:
                    # Update status
                    posts = self.load_queue()
                    for p in posts:
                        if p.id == post.id:
                            p.status = "published"
                            p.published_at = datetime.now(timezone.utc).isoformat()
                    self.save_queue(posts)

                    # Log to flight ledger
                    self.governor.record_action("company_post", {
                        "post_id": post.id,
                        "title": post.title
                    })
                    return True, f"Successfully published Post #{post.id} ('{post.title}')", post
                else:
                    return False, f"Failed to publish Post #{post.id} via browser pilot.", post

            finally:
                await browser.close()
