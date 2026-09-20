"""
Capture & Fallback Engine for DocuAgent AI.
Provides functions to capture screenshots and implement fallback mechanisms.
"""

from pathlib import Path

from playwright.async_api import Page

from app.config import settings
from app.state import ManualState


async def capture_viewport_screenshot(
    page: Page,
    job_id: str,
    step_index: int,
    state: ManualState | None = None,
) -> str:
    """
    Capture a viewport PNG screenshot and save it to the specified path.

    Args:
        page: Playwright Page object
        job_id: Unique identifier for the job
        step_index: Index of the step being captured (0-based)
        state: Optional ManualState to record failure diagnostics

    Returns:
        str: The file path where the screenshot was saved

    Raises:
        Exception: If screenshot capture fails
    """
    try:
        # Create the assets directory for this job if it doesn't exist
        assets_dir = Path(settings.assets_dir) / job_id
        assets_dir.mkdir(parents=True, exist_ok=True)

        # Define the file path with the required format: step_{index:03d}.png
        file_path = assets_dir / f"step_{step_index:03d}.png"

        # Capture the viewport screenshot
        await page.screenshot(path=str(file_path), full_page=False)

        # Clear any previous error for this step if state is provided
        if state is not None and "error_states" in state:
            error_states = state["error_states"].copy()
            if str(step_index) in error_states:
                del error_states[str(step_index)]
                # Note: In practice, the caller would handle state updates

        return str(file_path)
    except Exception as e:
        # Record failure diagnostics in state if provided
        if state is not None:
            if "error_states" not in state or state["error_states"] is None:
                state["error_states"] = {}
            state["error_states"][str(step_index)] = {
                "error": str(e),
                "error_type": type(e).__name__,
                "step_index": step_index,
                "job_id": job_id,
                "timestamp": str(Path(__file__)),
                "screenshot_type": "viewport",
            }

        # Re-raise the exception to maintain existing behavior
        raise


async def capture_screenshot_with_fallback(
    page: Page,
    job_id: str,
    step_index: int,
    primary_selector: str,
    selector_hints: list[str],
    state: ManualState | None = None,
    step_description: str | None = None,
) -> str:
    """
    Capture a screenshot with fallback mechanism.
    Try primary selector, then selector hints, then general viewport fallback.
    If all capture methods fail, generate a text placeholder.

    Args:
        page: Playwright Page object
        job_id: Unique identifier for the job
        step_index: Index of the step being captured (0-based)
        primary_selector: Primary CSS/XPath selector for the target element
        selector_hints: List of alternative selector strings (CSS/XPath) ordered by preference
        state: Optional ManualState to record failure diagnostics
        step_description: Optional description of the step for placeholder generation

    Returns:
        str: The file path where the screenshot was saved, or a text placeholder if all capture methods fail

    Note:
        This function attempts to capture a screenshot of a specific element first.
        If that fails, it tries the selector hints. If all selector-based attempts fail,
        it falls back to capturing the general viewport.
        If all capture methods fail (including viewport), it generates a text placeholder
        in the format "[Insert Screenshot Here: Description]".
        Failure diagnostics are recorded in state["error_states"][step.index] without
        breaking pipeline execution.
    """
    # Try primary selector first
    selectors_to_try = [primary_selector, *selector_hints]

    last_exception = None

    for selector in selectors_to_try:
        try:
            # Wait for the element to be present
            await page.wait_for_selector(selector, state="attached", timeout=5000)

            # If we get here, the element exists - capture element screenshot
            assets_dir = Path(settings.assets_dir) / job_id
            assets_dir.mkdir(parents=True, exist_ok=True)
            file_path = assets_dir / f"step_{step_index:03d}.png"

            # Capture screenshot of the specific element
            element = await page.query_selector(selector)
            if element:
                await element.screenshot(path=str(file_path))

                # Clear any previous error for this step if state is provided
                if state is not None and "error_states" in state:
                    error_states = state["error_states"].copy()
                    if str(step_index) in error_states:
                        del error_states[str(step_index)]

                return str(file_path)

        except Exception as e:
            # Store the last exception to potentially raise if all fail
            last_exception = e
            # Continue to next selector if this one fails
            continue

    # If all selector-based attempts failed, fall back to viewport screenshot
    try:
        result = await capture_viewport_screenshot(page, job_id, step_index, state)
        return result
    except Exception as e:
        # If viewport capture also fails, record the error and generate a text placeholder
        if state is not None:
            if "error_states" not in state or state["error_states"] is None:
                state["error_states"] = {}
            state["error_states"][str(step_index)] = {
                "error": str(e),
                "error_type": type(e).__name__,
                "step_index": step_index,
                "job_id": job_id,
                "timestamp": str(Path(__file__)),
                "screenshot_type": "viewport_fallback",
                "selectors_attempted": selectors_to_try,
                "last_exception": str(last_exception) if last_exception else None,
            }

        # Generate text placeholder if all capture methods fail
        # Use provided step description or generate a default one
        if step_description is None:
            step_description = f"Step {step_index}"

        # Return text placeholder in the internal format expected by the system
        return f"PLACEHOLDER:{step_description}"
