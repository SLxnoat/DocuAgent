"""
Dynamic Highlight & Overlay Injector for DocuAgent AI.
Provides functions to inject and remove visual highlighting effects for Playwright automation.
Includes target element verification against common frontend component patterns.
"""

from playwright.async_api import Page


async def inject_highlight_effects(page: Page, selector: str) -> None:
    """
    Inject visual highlighting effects for a target element.
    Includes verification against common frontend component patterns.

    Args:
        page: Playwright Page object
        selector: CSS selector for the target element to highlight
    """
    # Wait for the element to be present
    await page.wait_for_selector(selector, state="attached", timeout=5000)

    # Inject the highlight effects using page.evaluate
    await page.evaluate(
        r"""(selector) => {
        // Remove any existing highlights first to avoid duplication
        const existingHighlight = document.querySelector('.docuagent-highlight-overlay');
        if (existingHighlight) {
            existingHighlight.remove();
        }

        const existingBackdrop = document.querySelector('.docuagent-backdrop-overlay');
        if (existingBackdrop) {
            existingBackdrop.remove();
        }

        const targetElement = document.querySelector(selector);
        if (!targetElement) return;

        // Get element dimensions and position
        const rect = targetElement.getBoundingClientRect();

        // Verify element against common frontend component patterns
        const elementInfo = verifyElementPattern(targetElement);

        // Create highlight overlay for the target element
        const highlightOverlay = document.createElement('div');
        highlightOverlay.className = 'docuagent-highlight-overlay';
        highlightOverlay.style.position = 'fixed';
        highlightOverlay.style.left = `${rect.left + window.scrollX}px`;
        highlightOverlay.style.top = `${rect.top + window.scrollY}px`;
        highlightOverlay.style.width = `${rect.width}px`;
        highlightOverlay.style.height = `${rect.height}px`;

        // Adjust highlight style based on element type
        const { isKnownPattern, elementType, suggestedColor } = elementInfo;
        const baseColor = '#06b6d4'; // Default cyan
        const highlightColor = isKnownPattern ? baseColor : suggestedColor || '#ff6b6d'; // Reddish for unknown patterns

        highlightOverlay.style.outline = `4px solid ${highlightColor}`;
        highlightOverlay.style.boxShadow = `0 0 0 8px rgba(${hexToRgb(highlightColor)}, 0.2)`; // Glow effect
        highlightOverlay.style.pointerEvents = 'none';
        highlightOverlay.style.zIndex = '999999';
        highlightOverlay.style.borderRadius = '4px';

        // Create backdrop overlay for dimming non-target elements
        const backdropOverlay = document.createElement('div');
        backdropOverlay.className = 'docuagent-backdrop-overlay';
        backdropOverlay.style.position = 'fixed';
        backdropOverlay.style.top = '0';
        backdropOverlay.style.left = '0';
        backdropOverlay.style.width = '100vw';
        backdropOverlay.style.height = '100vh';
        backdropOverlay.style.backgroundColor = 'rgba(0, 0, 0, 0.15)'; // Dimming backdrop
        backdropOverlay.style.pointerEvents = 'none';
        backdropOverlay.style.zIndex = '999998';

        // Add outlines to make the overlay visible during positioning
        highlightOverlay.style.outline = `4px solid ${highlightColor}`;

        // Append to body
        document.body.appendChild(highlightOverlay);
        document.body.appendChild(backdropOverlay);

        // Helper function to convert hex color to rgb
        function hexToRgb(hex) {
            const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
            hex = hex.replace(shorthandRegex, (m, r, g, b) => r + r + g + g + b + b);

            const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            return result ?
                `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` :
                '0, 0, 0';
        }

        // Verify element against common frontend component patterns
        function verifyElementPattern(element) {
            // Common frontend component patterns
            const patterns = {
                button: ['BUTTON', 'INPUT[type="button"]', 'INPUT[type="submit"]', 'INPUT[type="reset"]'],
                link: ['A'],
                input: ['INPUT[type="text"]', 'INPUT[type="email"]', 'INPUT[type="password"]',
                       'INPUT[type="number"]', 'INPUT[type="tel"]', 'INPUT[type="url"]',
                       'INPUT[type="search"]', 'INPUT[type="date"]', 'INPUT[type="time"]'],
                textarea: ['TEXTAREA'],
                select: ['SELECT'],
                form: ['FORM'],
                div: ['DIV'],
                span: ['SPAN'],
                heading: ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'],
                image: ['IMG'],
                label: ['LABEL']
            };

            const tagName = element.tagName.toUpperCase();
            const className = element.className || '';
            const id = element.id || '';
            const type = element.type || '';

            // Check if element matches known patterns
            let isKnownPattern = false;
            let elementType = 'unknown';

            // Check by tag name and type
            for (const [type, selectors] of Object.entries(patterns)) {
                for (const selector of selectors) {
                    if (selector === tagName) {
                        isKnownPattern = true;
                        elementType = type;
                        break;
                    }
                    // Handle input types
                    if (selector.startsWith('INPUT[type="') && tagName === 'INPUT') {
                        const expectedType = selector.match(/INPUT\[type="([^"]+)"\]/)[1];
                        if (type === expectedType) {
                            isKnownPattern = true;
                            elementType = type;
                            break;
                        }
                    }
                }
                if (isKnownPattern) break;
            }

            // Additional heuristic checks for common component indicators
            const hasRole = element.getAttribute('role') !== null;
            const hasAriaLabel = element.getAttribute('aria-label') !== null;
            const hasTabindex = element.getAttribute('tabindex') !== null;
            const isClickable = element.onclick !== null ||
                             element.getAttribute('onclick') !== null ||
                             element.style.cursor === 'pointer';

            // If it has interactive attributes, consider it a known pattern even if tag is generic
            if (!isKnownPattern && (hasRole || hasAriaLabel || hasTabindex || isClickable)) {
                isKnownPattern = true;
                elementType = 'interactive';
            }

            // Suggest color based on element type (for unknown patterns)
            let suggestedColor = null;
            if (!isKnownPattern) {
                // Use different shades for different types of unknown elements
                const hash = simpleHash(tagName + className + id);
                const hue = (hash % 360); // 0-360 degrees
                suggestedColor = `hsl(${hue}, 70%, 50%)`; // Saturation 70%, lightness 50%
            }

            return {
                isKnownPattern,
                elementType,
                suggestedColor,
                details: {
                    tagName,
                    className,
                    id,
                    type,
                    hasRole,
                    hasAriaLabel,
                    hasTabindex,
                    isClickable
                }
            };
        }

        // Simple hash function for consistent color generation
        function simpleHash(str) {
            let hash = 0;
            for (let i = 0; i < str.length; i++) {
                const char = str.charCodeAt(i);
                hash = ((hash << 5) - hash) + char;
                hash = hash & hash; // Convert to 32bit integer
            }
            return Math.abs(hash);
        }
    }""",
        selector,
    )


async def remove_highlight_effects(page: Page) -> None:
    """
    Remove all injected highlight and overlay effects.

    Args:
        page: Playwright Page object
    """
    await page.evaluate("""() => {
        // Remove highlight overlays
        const highlights = document.querySelectorAll('.docuagent-highlight-overlay');
        highlights.forEach(el => el.remove());

        // Remove backdrop overlays
        const backdrops = document.querySelectorAll('.docuagent-backdrop-overlay');
        backdrops.forEach(el => el.remove());
    }""")


async def cleanup_highlights(page: Page) -> None:
    """
    Clean up highlight effects - alias for remove_highlight_effects for clarity.
    This function is intended to be called before taking subsequent steps
    to remove injected DOM artifacts.

    Args:
        page: Playwright Page object
    """
    await remove_highlight_effects(page)


# Convenient alias
inject_highlight = inject_highlight_effects
