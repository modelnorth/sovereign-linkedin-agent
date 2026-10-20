"""
ModelNorth Sovereign LinkedIn Agent - Company Page Management Engine
https://modelnorth.com

Automates high-ticket thought leadership distribution for ModelNorth:
- Company feed publishing with rich media and graphics.
- Technical carousel PDF distribution.
- Automated feed verification and engagement auditing.
"""

import asyncio
import logging
import random
from pathlib import Path
from typing import Optional
from sovereign_linkedin.config import AgentConfig
from sovereign_linkedin.engine.browser import BrowserDriver
from sovereign_linkedin.core.stealth import StealthEngine

logger = logging.getLogger("sovereign_linkedin.company_page")


class CompanyPagePilot:
    def __init__(self, config: AgentConfig, browser: BrowserDriver):
        self.config = config
        self.browser = browser
        self.admin_url = f"https://www.linkedin.com/company/{config.brand.company_urn}/admin/dashboard/"
        self.public_url = f"https://www.linkedin.com/company/{config.brand.company_vanity}/"

    async def open_company_admin(self) -> None:
        """Navigates to ModelNorth company page admin dashboard."""
        page = await self.browser.navigate_safely(self.admin_url, wait_selector="main")
        logger.info("Company page admin dashboard loaded.")

    async def publish_company_post(
        self,
        post_text: str,
        media_path: Optional[Path] = None
    ) -> bool:
        """
        Publishes a post directly to the ModelNorth company page feed.
        Supports optional image/graphic attachment.
        """
        page = await self.browser.get_or_create_page()
        await self.open_company_admin()
        await asyncio.sleep(random.uniform(2.0, 3.5))

        # Look for "Start a post" button
        composer_triggers = [
            "button:has-text('Start a post')",
            "div.share-box-feed-entry__top-bar",
            "button.share-box-feed-entry__trigger"
        ]

        opened = False
        for selector in composer_triggers:
            if await page.locator(selector).count() > 0:
                await StealthEngine.human_move_and_click(page, selector)
                opened = True
                break

        if not opened:
            logger.error("Could not locate 'Start a post' trigger on company dashboard.")
            return False

        # Wait for modal editor
        editor_selector = "div.ql-editor[contenteditable='true'], div[role='textbox']"
        await page.wait_for_selector(editor_selector, timeout=10000)

        # Upload media if provided
        if media_path and Path(media_path).exists():
            file_input = page.locator("input[type='file']")
            if await file_input.count() > 0:
                logger.info(f"Uploading media attachment: {media_path}")
                await file_input.set_input_files(str(media_path))
                await asyncio.sleep(random.uniform(2.5, 4.0))
                # If there's an image modal 'Next' button
                next_btn = page.locator("button:has-text('Next')")
                if await next_btn.count() > 0:
                    await next_btn.click()
                    await asyncio.sleep(random.uniform(1.0, 2.0))

        # Human type post text
        await StealthEngine.human_type(page, editor_selector, post_text)
        await asyncio.sleep(random.uniform(1.5, 3.0))

        # Locate and click 'Post' button
        post_btn = page.locator("button.share-actions__primary-action, button:has-text('Post')").last
        await post_btn.click()
        logger.info("Submitted post to company feed. Waiting for confirmation...")
        await asyncio.sleep(random.uniform(3.5, 6.0))

        return True
