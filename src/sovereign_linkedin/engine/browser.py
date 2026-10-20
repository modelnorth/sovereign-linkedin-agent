"""
ModelNorth Sovereign LinkedIn Agent - Browser Automation Driver
https://modelnorth.com

Manages resilient, anti-ban browser sessions:
- Attaches to local authenticated Brave browser over CDP.
- Alternatively launches a stealth Playwright/Patchright instance.
- Automatically injects anti-fingerprint cloaking scripts before page loads.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from sovereign_linkedin.config import AgentConfig
from sovereign_linkedin.core.stealth import StealthEngine

logger = logging.getLogger("sovereign_linkedin.browser")


class BrowserDriver:
    def __init__(self, config: AgentConfig):
        self.config = config
        self._playwright: Optional[Any] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    async def connect_cdp(self) -> Page:
        """Connect to an existing authenticated Brave/Chrome browser via CDP."""
        self._playwright = await async_playwright().start()
        cdp_url = self.config.browser.cdp_url
        logger.info(f"Connecting to live browser via CDP at: {cdp_url}")
        try:
            self._browser = await self._playwright.chromium.connect_over_cdp(cdp_url)
            # Fetch default context or active page
            contexts = self._browser.contexts
            if contexts:
                self._context = contexts[0]
            else:
                self._context = await self._browser.new_context()

            pages = self._context.pages
            if pages:
                self._page = pages[0]
            else:
                self._page = await self._context.new_page()

            # Inject stealth cloaking
            await self._page.add_init_script(StealthEngine.STEALTH_JS)
            logger.info("Connected to CDP browser successfully.")
            return self._page
        except Exception as e:
            logger.error(f"Failed to connect to CDP at {cdp_url}: {e}")
            raise

    async def launch_stealth(self) -> Page:
        """Launch a standalone persistent browser instance with anti-ban protections."""
        self._playwright = await async_playwright().start()
        profile_path = self.config.browser.user_data_dir
        profile_path.mkdir(parents=True, exist_ok=True)

        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-infobars",
            "--window-size=1440,900"
        ]

        logger.info(f"Launching standalone stealth browser with profile at {profile_path}")
        self._context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            headless=self.config.browser.headless,
            args=launch_args,
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            )
        )
        pages = self._context.pages
        self._page = pages[0] if pages else await self._context.new_page()
        await self._page.add_init_script(StealthEngine.STEALTH_JS)
        return self._page

    async def get_or_create_page(self) -> Page:
        if self._page and not self._page.is_closed():
            return self._page
        if self.config.browser.browser_type == "cdp":
            return await self.connect_cdp()
        return await self.launch_stealth()

    async def navigate_safely(self, url: str, wait_selector: Optional[str] = None) -> Page:
        """Navigates with human randomized delay and wait conditions."""
        page = await self.get_or_create_page()
        logger.info(f"Navigating to {url}")
        await page.goto(url, wait_until="domcontentloaded")
        if wait_selector:
            await page.wait_for_selector(wait_selector, timeout=15000)
        await asyncio.sleep(random.uniform(1.5, 3.0))
        return page

    async def capture_audit(self, output_path: Path) -> Path:
        """Captures page screenshot for visual audit and verification."""
        page = await self.get_or_create_page()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(output_path), full_page=False)
        logger.info(f"Saved audit screenshot to {output_path}")
        return output_path

    async def close(self) -> None:
        try:
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception as e:
            logger.debug(f"Error during browser teardown: {e}")
