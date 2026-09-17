"""
Playwright Capture Engine for DocuAgent AI.
Provides an async context manager for browser automation using Playwright.
"""

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from app.config import settings


class PlaywrightCaptureEngine:
    """
    Async context manager for Playwright browser automation.

    Handles browser launch, context creation, and cleanup.
    """

    def __init__(self):
        """Initialize the Playwright capture engine."""
        self.playwright = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    async def __aenter__(self) -> "PlaywrightCaptureEngine":
        """
        Enter the async context, launching browser and creating context.

        Returns:
            Self instance for use within the context.
        """
        self.playwright = await async_playwright().start()

        # Launch browser with configured arguments
        self.browser = await self.playwright.chromium.launch(
            headless=settings.playwright_headless,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                f"--window-size={settings.playwright_viewport_width},{settings.playwright_viewport_height}",
            ],
        )

        # Create browser context with configured settings
        self.context = await self.browser.new_context(
            viewport={
                "width": settings.playwright_viewport_width,
                "height": settings.playwright_viewport_height,
            },
            locale="en-US",
            ignore_https_errors=True,
        )

        # Create a new page
        self.page = await self.context.new_page()

        # Set default timeout for selectors
        self.page.set_default_timeout(settings.playwright_selector_timeout_ms)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the async context, cleaning up resources.

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Traceback if an error occurred
        """
        if self.page:
            await self.page.close()

        if self.context:
            await self.context.close()

        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()

    # Additional methods can be added here for specific actions
    # like navigate, click, type, etc., which would be used by Agent 2
