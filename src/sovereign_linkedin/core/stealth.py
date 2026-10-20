"""
ModelNorth Sovereign LinkedIn Agent - Anti-Ban Stealth & Human Telemetry Engine
https://modelnorth.com

Defeats PerimeterX, Akamai, and LinkedIn anti-automation detection:
1. Strips navigator.webdriver and CDP automation hooks.
2. Injects human-like Bezier curve mouse trajectory with stochastic micro-jitter.
3. Simulates realistic keystroke latency with Gaussian typing cadences.
4. Smooth multi-stage non-linear viewport scrolling.
"""

import asyncio
import math
import random
import time
from typing import Any, Optional


class StealthEngine:
    """Anti-detection telemetry emulator."""

    STEALTH_JS = """
    (() => {
        // 1. Strip navigator.webdriver flag
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
            configurable: true
        });

        // 2. Mock plugins array
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
            configurable: true
        });

        // 3. Mock languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en', 'ar'],
            configurable: true
        });

        // 4. Clean window.chrome runtime
        if (!window.chrome) {
            window.chrome = {};
        }
        if (!window.chrome.runtime) {
            window.chrome.runtime = {};
        }

        // 5. Mask WebGL vendor strings
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return 'Google Inc. (NVIDIA)';
            }
            if (parameter === 37446) {
                return 'ANGLE (NVIDIA, NVIDIA GeForce RTX 4090 Direct3D11 vs_5_0 ps_5_0)';
            }
            return getParameter.apply(this, arguments);
        };
    })();
    """

    @staticmethod
    def get_typing_delay(char: str, min_ms: int = 40, max_ms: int = 110) -> float:
        """Calculate human typing delay with micro-pauses at punctuation."""
        base_delay = random.uniform(min_ms / 1000.0, max_ms / 1000.0)
        if char in {".", ",", "!", "?", "\n"}:
            return base_delay + random.uniform(0.20, 0.45)
        elif char in {" ", "-", "_"}:
            return base_delay + random.uniform(0.05, 0.12)
        return base_delay

    @staticmethod
    async def human_type(page: Any, selector: str, text: str, min_ms: int = 40, max_ms: int = 110) -> None:
        """Types text character-by-character simulating natural human biomechanics."""
        element = page.locator(selector)
        await element.click()
        await asyncio.sleep(random.uniform(0.15, 0.35))

        for char in text:
            await page.keyboard.type(char, delay=0)
            await asyncio.sleep(StealthEngine.get_typing_delay(char, min_ms, max_ms))

    @staticmethod
    async def human_scroll(page: Any, scroll_distance: int = 600, steps: int = 5) -> None:
        """Scrolls viewport in non-linear increments to trigger lazy-load telemetry naturally."""
        direction = 1 if scroll_distance > 0 else -1
        remaining = abs(scroll_distance)

        for _ in range(steps):
            if remaining <= 0:
                break
            chunk = int(random.uniform(0.15, 0.35) * remaining)
            if chunk == 0:
                chunk = remaining
            await page.mouse.wheel(0, chunk * direction)
            remaining -= chunk
            await asyncio.sleep(random.uniform(0.12, 0.30))

        await asyncio.sleep(random.uniform(0.4, 0.8))

    @staticmethod
    def calculate_bezier_trajectory(
        start: tuple[float, float],
        end: tuple[float, float],
        points: int = 25
    ) -> list[tuple[float, float]]:
        """Generates realistic human mouse path using cubic Bezier curves with jitter."""
        x0, y0 = start
        x3, y3 = end

        # Generate stochastic control points
        dx = x3 - x0
        dy = y3 - y0
        deviation = random.uniform(0.15, 0.35) * math.hypot(dx, dy)

        x1 = x0 + dx * 0.25 + random.uniform(-deviation, deviation)
        y1 = y0 + dy * 0.25 + random.uniform(-deviation, deviation)
        x2 = x0 + dx * 0.75 + random.uniform(-deviation, deviation)
        y2 = y0 + dy * 0.75 + random.uniform(-deviation, deviation)

        trajectory: list[tuple[float, float]] = []
        for i in range(points + 1):
            t = i / float(points)
            # Cubic Bezier formula
            x = (1 - t)**3 * x0 + 3 * (1 - t)**2 * t * x1 + 3 * (1 - t) * t**2 * x2 + t**3 * x3
            y = (1 - t)**3 * y0 + 3 * (1 - t)**2 * t * y1 + 3 * (1 - t) * t**2 * y2
            # Add subtle biomechanical jitter
            jitter = random.uniform(-1.2, 1.2) if 0 < i < points else 0
            trajectory.append((x + jitter, y + jitter))

        return trajectory

    @staticmethod
    async def human_move_and_click(page: Any, target_selector: str) -> None:
        """Smoothly moves cursor along Bezier curve to target element and executes click."""
        element = page.locator(target_selector).first
        box = await element.bounding_box()
        if not box:
            await element.click()
            return

        # Target center with random micro-offset
        target_x = box["x"] + box["width"] * random.uniform(0.35, 0.65)
        target_y = box["y"] + box["height"] * random.uniform(0.35, 0.65)

        # Approximate current mouse position (fallback to random point in viewport)
        start_x = random.uniform(100, 400)
        start_y = random.uniform(100, 300)

        path = StealthEngine.calculate_bezier_trajectory((start_x, start_y), (target_x, target_y))
        for px, py in path:
            await page.mouse.move(px, py)
            await asyncio.sleep(random.uniform(0.008, 0.022))

        await asyncio.sleep(random.uniform(0.08, 0.20))
        await page.mouse.down()
        await asyncio.sleep(random.uniform(0.04, 0.11))
        await page.mouse.up()
        await asyncio.sleep(random.uniform(0.15, 0.35))
