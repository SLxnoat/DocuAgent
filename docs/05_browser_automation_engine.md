# Browser Automation Engine

**Document ID:** DOC-005  
**Version:** 1.0.0  
**Status:** Approved  
**Last Updated:** September 2026  
**Audience:** Backend Engineers, QA Engineers

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture & Integration](#2-architecture--integration)
3. [Browser Initialization](#3-browser-initialization)
4. [Authentication & Session Management](#4-authentication--session-management)
5. [Step Execution Logic](#5-step-execution-logic)
6. [Dynamic Highlight Engine](#6-dynamic-highlight-engine)
7. [Screenshot Capture](#7-screenshot-capture)
8. [Fallback Strategies](#8-fallback-strategies)
9. [Manual Screenshot Replacement](#9-manual-screenshot-replacement)
10. [Selector Strategy Reference](#10-selector-strategy-reference)
11. [Configuration Reference](#11-configuration-reference)
12. [Performance Considerations](#12-performance-considerations)

---

## 1. Overview

The **Playwright Visual Capture Engine** is the browser automation subsystem responsible for executing live UI workflows against staging application environments, annotating target UI elements with visual highlights, and capturing high-resolution screenshots mapped to each manual step.

### 1.1 Key Capabilities

| Capability | Description |
|-----------|-------------|
| **Headless Browser Execution** | Uses Chromium in headless mode for server-side screenshot capture |
| **Dynamic DOM Highlighting** | Injects real-time CSS outlines and overlays to annotate target elements |
| **Multi-Browser Compatibility** | Supports Chromium, Firefox, and WebKit via Playwright API |
| **Auth Session Injection** | Supports username/password login and browser storage-based session injection |
| **Viewport Auto-Scroll** | Scrolls target elements into center viewport before capture |
| **Graceful Fallback** | Continues pipeline on selector failure with a full-viewport fallback screenshot |

### 1.2 Technology

| Component | Technology | Version |
|-----------|-----------|---------|
| Browser Engine | Playwright Python SDK (Chromium) | 1.40+ |
| Python Runtime | Python 3.11+ | 3.11+ |
| Async Interface | `asyncio` + `playwright.async_api` | — |

---

## 2. Architecture & Integration

The capture engine is invoked exclusively by **Agent 2 (Playwright Visual Capturer)** within the LangGraph state machine. It operates as a managed async context within the Python backend process.

```
LangGraph Agent 2 (capture_screenshots_node)
                │
                ▼
    PlaywrightCaptureEngine.capture_all_steps(
        steps=state["structured_steps"],
        target_url=state["target_url"],
        credentials=state["credentials"],
        job_id=state["job_id"]
    )
                │
                ├── Browser context initialized
                │
                ├── Step 1: authenticate()
                │
                └── For each StepSchema:
                        │
                        ├── execute_action(step)
                        ├── highlight_element(step.target_selector)
                        ├── capture_screenshot(step.index)
                        └── register_asset(step.index, file_path)
                │
                ▼
    Returns: dict[int, str]  →  screenshot_assets
```

---

## 3. Browser Initialization

```python
import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

class PlaywrightCaptureEngine:
    
    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self.browser: Browser = await self._playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1440,900",
            ]
        )
        self.context: BrowserContext = await self.browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="en-US",
            timezone_id="Asia/Colombo",
            ignore_https_errors=True,     # Allow staging self-signed certs
        )
        self.page: Page = await self.context.new_page()
        return self
    
    async def __aexit__(self, *args):
        await self.browser.close()
        await self._playwright.stop()
```

### 3.1 Browser Configuration Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `headless` | `True` | Server-side execution without display |
| `viewport` | `1440×900` | Standard widescreen resolution |
| `ignore_https_errors` | `True` | Staging environments often use self-signed certificates |
| `--no-sandbox` | enabled | Required for containerized environments (Docker) |
| `locale` | `en-US` | Consistent UI language rendering |

---

## 4. Authentication & Session Management

### 4.1 Form-Based Authentication

For applications using standard login forms:

```python
async def authenticate(self, credentials: dict, login_url: str):
    """Perform form-based login and wait for successful navigation."""
    await self.page.goto(login_url, wait_until="networkidle")
    
    # Primary selectors with fallbacks
    username_selectors = [
        "input[name='username']",
        "input[type='email']",
        "#username",
        "[data-testid='username-input']"
    ]
    password_selectors = [
        "input[name='password']",
        "input[type='password']",
        "#password",
        "[data-testid='password-input']"
    ]
    
    await self._fill_first_matching(username_selectors, credentials["username"])
    await self._fill_first_matching(password_selectors, credentials["password"])
    
    # Submit form
    await self.page.keyboard.press("Enter")
    await self.page.wait_for_load_state("networkidle", timeout=30000)
```

### 4.2 Session Storage Injection

For applications supporting token-based auth or pre-authenticated sessions:

```python
async def inject_session(self, session_data: dict):
    """Inject pre-authenticated session into browser storage."""
    await self.context.add_init_script(f"""
        window.localStorage.setItem('auth_token', '{session_data.get("token", "")}');
        window.sessionStorage.setItem('session_id', '{session_data.get("session_id", "")}');
    """)
```

### 4.3 🔒 Credential Security

> ⚠️ **Warning:** Credentials are passed to this engine exclusively from `ManualState.credentials`. They exist only in process memory during execution and are **never written to disk, logged, or persisted** in any form.

```python
# Credentials are cleared from state by Agent 2 immediately after use
state["credentials"] = {}  # Scrub from LangGraph state before checkpoint
```

---

## 5. Step Execution Logic

Each `StepSchema` is executed by a dispatcher that maps `action_type` to the appropriate Playwright call:

```python
async def execute_action(self, step: StepSchema) -> None:
    """Dispatch browser action based on step action_type."""
    
    action_map = {
        "navigate":     self._action_navigate,
        "click":        self._action_click,
        "type":         self._action_type,
        "scroll":       self._action_scroll,
        "wait":         self._action_wait,
        "authenticate": self._action_authenticate,
    }
    
    handler = action_map.get(step.action_type)
    if not handler:
        raise ValueError(f"Unknown action_type: {step.action_type}")
    
    await handler(step)


async def _action_navigate(self, step: StepSchema):
    await self.page.goto(step.input_value, wait_until="networkidle", timeout=30000)

async def _action_click(self, step: StepSchema):
    element = await self._locate_element(step.target_selector, step.selector_hints)
    await element.scroll_into_view_if_needed()
    await element.click()
    await self.page.wait_for_load_state("networkidle", timeout=15000)

async def _action_type(self, step: StepSchema):
    element = await self._locate_element(step.target_selector, step.selector_hints)
    await element.clear()
    await element.type(step.input_value, delay=50)  # 50ms delay mimics human typing

async def _action_scroll(self, step: StepSchema):
    await self.page.evaluate(f"document.querySelector('{step.target_selector}').scrollIntoView({{block: 'center'}})")

async def _action_wait(self, step: StepSchema):
    await self.page.wait_for_timeout(int(step.input_value or 1000))
```

---

## 6. Dynamic Highlight Engine

The highlight engine applies real-time CSS modifications to the live DOM before capturing each screenshot. This annotates exactly which UI element the manual step refers to.

### 6.1 Highlight Injection

```python
async def highlight_element(self, selector: str) -> bool:
    """
    Inject visual highlight styles onto the target element.
    
    Returns True if element was found and highlighted; False otherwise.
    """
    try:
        await self.page.evaluate(f"""
            (() => {{
                // Remove any existing highlights
                document.querySelectorAll('[data-docuagent-highlight]').forEach(el => {{
                    el.removeAttribute('style');
                    el.removeAttribute('data-docuagent-highlight');
                }});
                
                // Apply highlight to target element
                const target = document.querySelector('{selector}');
                if (!target) return false;
                
                // Scroll target into center viewport
                target.scrollIntoView({{ behavior: 'instant', block: 'center' }});
                
                // Apply highlight styles
                target.setAttribute('data-docuagent-highlight', 'true');
                target.style.outline = '4px solid #06b6d4';        // Cyan border
                target.style.outlineOffset = '2px';
                target.style.boxShadow = '0 0 0 8px rgba(6, 182, 212, 0.2)';  // Glow effect
                target.style.borderRadius = '4px';
                target.style.transition = 'none';
                
                // Dim non-target regions (semi-transparent overlay on body)
                const overlay = document.createElement('div');
                overlay.setAttribute('data-docuagent-overlay', 'true');
                overlay.style.cssText = `
                    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                    background: rgba(0, 0, 0, 0.15); pointer-events: none; z-index: 9998;
                `;
                document.body.appendChild(overlay);
                
                return true;
            }})()
        """)
        return True
    except Exception as e:
        self._log(f"Highlight injection failed for selector '{selector}': {e}")
        return False
```

### 6.2 Highlight Cleanup

After capturing the screenshot, all injected styles are removed to avoid contaminating subsequent steps:

```python
async def cleanup_highlights(self):
    """Remove all docuagent injected styles and overlays."""
    await self.page.evaluate("""
        document.querySelectorAll('[data-docuagent-highlight]').forEach(el => {
            el.style.removeProperty('outline');
            el.style.removeProperty('outline-offset');
            el.style.removeProperty('box-shadow');
            el.style.removeProperty('border-radius');
            el.removeAttribute('data-docuagent-highlight');
        });
        document.querySelectorAll('[data-docuagent-overlay]').forEach(el => el.remove());
    """)
```

### 6.3 Highlight Visual Specification

| Style Property | Value | Purpose |
|---------------|-------|---------|
| `outline` | `4px solid #06b6d4` | Cyan border — high contrast on both light and dark UIs |
| `outlineOffset` | `2px` | Small gap between element boundary and outline |
| `boxShadow` | `0 0 0 8px rgba(6,182,212,0.2)` | Soft glow effect to increase visibility |
| `borderRadius` | `4px` | Smooth corner rounding to match modern UI aesthetics |
| Background overlay opacity | `0.15` | Subtle darkening without obscuring context |

---

## 7. Screenshot Capture

### 7.1 Capture Sequence

```python
async def capture_screenshot(self, step_index: int, job_id: str) -> str:
    """
    Capture a full-page or viewport screenshot and save to disk.
    
    Returns the absolute file path of the saved screenshot.
    """
    output_dir = Path(f"assets/{job_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = output_dir / f"step_{step_index:03d}.png"
    
    await self.page.screenshot(
        path=str(file_path),
        full_page=False,       # Viewport only — preserves highlight position context
        type="png",
        animations="disabled"  # Freeze animations for clean capture
    )
    
    return str(file_path)
```

### 7.2 Screenshot Specifications

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Format | PNG | Lossless — preserves highlight color accuracy |
| Capture Area | Viewport (1440×900) | Matches the rendered UI experience |
| `animations` | `disabled` | Prevents motion blur from CSS transitions |
| `full_page` | `False` | Target element is scrolled into viewport; full-page can shift context |

### 7.3 File Naming Convention

```
/assets/{job_id}/step_{index:03d}.png

Examples:
  /assets/job_a1b2c3d4e5f6/step_001.png   # Step 1 — primary capture
  /assets/job_a1b2c3d4e5f6/step_003.png   # Step 3 — primary capture
  /assets/job_a1b2c3d4e5f6/step_003_fallback.png  # Step 3 — fallback (selector failed)
```

---

## 8. Fallback Strategies

### 8.1 Selector Timeout Fallback

If a target selector cannot be located within the configured timeout, the engine uses the following fallback sequence:

```
Primary selector → timeout exceeded?
        │ YES
        ▼
Try selector_hints[0] → timeout exceeded?
        │ YES
        ▼
Try selector_hints[1] → timeout exceeded?
        │ YES
        ▼
Log warning to ManualState.error_states[step_index]
Take full-viewport screenshot (no highlight)
Save as step_{index:03d}_fallback.png
Continue to next step — pipeline does NOT abort
```

### 8.2 Fallback Implementation

```python
async def _locate_element(self, selector: str, fallback_selectors: list[str]):
    """Locate element with primary selector and fallback chain."""
    all_selectors = [selector] + (fallback_selectors or [])
    
    for sel in all_selectors:
        try:
            element = await self.page.wait_for_selector(sel, timeout=10000)
            if element:
                return element
        except Exception:
            continue
    
    raise ElementNotFoundError(f"None of the selectors matched: {all_selectors}")
```

### 8.3 Anti-Bot & Dynamic SPA Considerations

| Challenge | Strategy |
|-----------|---------|
| Client-side render delay | Use `wait_for_load_state("networkidle")` after navigation |
| Shadow DOM elements | Use Playwright's `>>` shadow piercing syntax in selectors |
| Dynamic class names | Use `[data-testid]` attributes or `:has-text()` pseudo-selectors |
| Anti-bot detection | Use `stealth` browser launch args; rotate `user_agent` strings |
| CAPTCHA blocks | Log error; insert `[Insert Screenshot Here]` placeholder in document |

### 8.4 Graceful Degradation Text Placeholder

When a step produces a fallback screenshot or no screenshot at all, Agent 3 inserts a descriptive placeholder in the Markdown output:

```markdown
![Insert Screenshot Here: Step 3 — Click the 'Add New User' button in the Users section toolbar]()
```

This ensures the manual document remains complete and usable even when browser automation encounters obstacles.

---

## 9. Manual Screenshot Replacement

Users can replace any generated screenshot by clicking on it in the React editor:

### 9.1 Replacement Flow

```
User clicks screenshot in Preview panel
         │
         ▼
React renders file upload overlay on that image
         │
         ▼
User selects local PNG/JPG file
         │
         ▼
File uploaded to: POST /api/v1/jobs/{job_id}/assets/{step_index}
         │
         ▼
Server saves file to /assets/{job_id}/step_{index:03d}.png (overwrite)
         │
         ▼
ManualState.screenshot_assets updated
         │
         ▼
SSE event: {"type": "asset_replaced", "step_index": N}
         │
         ▼
React refreshes preview image
```

### 9.2 Upload Endpoint

```http
POST /api/v1/jobs/{job_id}/assets/{step_index}
Content-Type: multipart/form-data

Body: file=@screenshot.png

Response 200:
{
  "step_index": 3,
  "file_path": "/assets/job_a1b2c3d4e5f6/step_003.png",
  "timestamp": "2026-09-15T14:45:00+05:30"
}
```

---

## 10. Selector Strategy Reference

Recommended selector patterns for common UI element types:

| Element Type | Recommended Selector | Example |
|-------------|---------------------|---------|
| Buttons | `button:has-text("Label")` | `button:has-text("Save")` |
| Navigation links | `nav a[href="/path"]` | `nav a[href="/users"]` |
| Form inputs | `input[name="fieldname"]` | `input[name="email"]` |
| Test-ID attributes | `[data-testid="id"]` | `[data-testid="add-user-btn"]` |
| ARIA labels | `[aria-label="label"]` | `[aria-label="Close dialog"]` |
| Dropdowns | `select[name="fieldname"]` | `select[name="role"]` |
| Checkboxes | `input[type="checkbox"][name="n"]` | `input[type="checkbox"][name="active"]` |
| Modal dialogs | `.modal:visible >> button` | `.modal:visible >> button:has-text("Confirm")` |
| Shadow DOM | `host-element >> inner-element` | `my-component >> .inner-btn` |

---

## 11. Configuration Reference

The capture engine is configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PLAYWRIGHT_BROWSER` | `chromium` | Browser engine: `chromium`, `firefox`, `webkit` |
| `PLAYWRIGHT_HEADLESS` | `true` | Run browser headlessly |
| `PLAYWRIGHT_VIEWPORT_WIDTH` | `1440` | Browser viewport width in pixels |
| `PLAYWRIGHT_VIEWPORT_HEIGHT` | `900` | Browser viewport height in pixels |
| `PLAYWRIGHT_SELECTOR_TIMEOUT_MS` | `10000` | Per-selector timeout in milliseconds |
| `PLAYWRIGHT_NAVIGATION_TIMEOUT_MS` | `30000` | Page navigation timeout in milliseconds |
| `PLAYWRIGHT_SCREENSHOT_DIR` | `./assets` | Base directory for screenshot storage |
| `PLAYWRIGHT_HIGHLIGHT_COLOR` | `#06b6d4` | Hex color for element highlight outlines |
| `PLAYWRIGHT_HIGHLIGHT_OPACITY` | `0.15` | Background overlay opacity (0.0–1.0) |
| `PLAYWRIGHT_MAX_RETRIES` | `2` | Selector retry attempts before fallback |

---

## 12. Performance Considerations

### 12.1 Async Execution

The capture engine uses Python's `asyncio` with Playwright's async API. For multi-step workflows, steps are executed **sequentially** within a single browser context to maintain session state across steps (login → navigate → click sequence).

### 12.2 Worker Pool for Multi-Tenant

Concurrent generation jobs are isolated using separate **Celery worker processes**, each with its own Playwright browser instance. This prevents cross-job state contamination.

```
Job A ──► Celery Worker 1 ──► Playwright Browser Instance A
Job B ──► Celery Worker 2 ──► Playwright Browser Instance B
Job C ──► Celery Worker 3 ──► Playwright Browser Instance C
```

### 12.3 Resource Limits

| Resource | Recommended Limit | Notes |
|----------|------------------|-------|
| Concurrent browser instances | 5 (per server) | Each Chromium instance uses ~200MB RAM |
| Max steps per job | 50 | Prevents runaway automation loops |
| Screenshot file size | ~500KB avg (PNG) | 1440×900 viewport |
| Selector timeout | 10 seconds | Balance between reliability and speed |
| Job timeout (total) | 10 minutes | Hard-kill fallback for stuck jobs |

### 12.4 💡 Optimization Tips

- Use `data-testid` attributes in staging environments for highly stable selectors.
- Pre-inject auth tokens via `context.add_cookies()` to skip login steps where possible.
- Set `wait_for_load_state("domcontentloaded")` instead of `"networkidle"` for faster navigation in SPAs with persistent background requests.

---

*← Previous: [API Reference](./04_api_reference.md)*  
*→ Next: [Frontend Developer Guide](./06_frontend_developer_guide.md)*

---

*Document ID: DOC-005 · Version: 1.0.0 · DocuAgent AI Technical Documentation Suite*
