"""
Chat Refiner Agent for DocuAgent AI.
Handles classifying user chat messages and updating the markdown document accordingly.
"""

import re
from typing import Literal

from .llm import ollama_generate_text


def classify_chat_edit(
    message: str,
) -> Literal["text_edit", "structural_revision", "recapture_trigger"]:
    """
    Classify a user chat message into one of three edit types:
    - text_edit: simple textual changes (e.g., fix a typo, reword a sentence)
    - structural_revision: changes that affect the structure (e.g., add/remove a step, reorder steps)
    - recapture_trigger: requests to re-capture a screenshot for a specific step

    Args:
        message: The user's chat message.

    Returns:
        One of: "text_edit", "structural_revision", "recapture_trigger"
    """
    # Convert to lowercase for case-insensitive matching
    msg_lower = message.lower()

    # Keywords for recapture triggers
    recapture_keywords = [
        "recapture",
        "retake",
        "reshoot",
        "retake screenshot",
        "retake image",
        "replace screenshot",
        "update screenshot",
        "change screenshot",
        "retake picture",
        "reshoot image",
        "capture again",
        "screenshot again",
    ]

    # Check for recapture triggers first (more specific)
    if any(keyword in msg_lower for keyword in recapture_keywords):
        # Additionally, check for step reference to increase confidence
        step_reference_indicators = ["step", "stage", "phase", "number", "#"]
        if any(indicator in msg_lower for indicator in step_reference_indicators):
            return "recapture_trigger"
        # Even without explicit step reference, if recapture keywords are present, classify as recapture
        return "recapture_trigger"

    # Keywords for structural revisions
    structural_keywords = [
        "add",
        "remove",
        "delete",
        "insert",
        "move",
        "reorder",
        "rearrange",
        "step",
        "section",
        "subsection",
        "part",
        "chapter",
        "reorganize",
        "restructure",
        "modify structure",
        "change order",
        "swap",
        "insert step",
        "delete step",
        "remove step",
        "add step",
    ]

    # Check for structural revisions
    if any(keyword in msg_lower for keyword in structural_keywords):
        # Additional context: if it's about steps or structure
        structural_context = ["step", "section", "part", "chapter", "order", "sequence"]
        if any(context in msg_lower for context in structural_context):
            return "structural_revision"
        # If structural keywords are present, likely a structural revision
        return "structural_revision"

    # Default to text edit for anything else
    return "text_edit"


def update_markdown_sections(markdown: str, updates: dict[str, str]) -> str:
    """
    Update the markdown content by replacing the content under the specified headers.
    This function updates only the content blocks under the given headers, leaving
    the headers and other sections unchanged.

    Args:
        markdown: The original markdown string.
        updates: A dictionary mapping section headers (the text part of the header,
                 e.g., "Prerequisites" for "## Prerequisites") to the new content
                 for that section (as a string, which may include newlines).

    Returns:
        The updated markdown string with only the specified sections updated.

    Example:
        updates = {
            "Prerequisites": "Updated prerequisites content.",
            "Step-by-Step Walkthrough": "Updated walkthrough content."
        }
        new_markdown = update_markdown_sections(markdown, updates)
    """
    if not markdown or not updates:
        return markdown

    # Normalize the update keys for case-insensitive and whitespace-insensitive matching
    updates_normalized = {key.strip().lower(): value for key, value in updates.items()}

    # Split the markdown by headers, keeping the headers as separate items.
    # Pattern matches lines that start with 1-6 '#' characters followed by a space and then text.
    header_pattern = r"(^#{1,6} .+$)"
    parts = re.split(header_pattern, markdown, flags=re.MULTILINE)

    # If the markdown does not start with a header, the first part is the preamble.
    # We'll keep it as is.
    result_parts = []
    if parts[0]:  # Preamble before the first header
        result_parts.append(parts[0])

    # Process the parts in pairs: (header, content)
    # If the number of parts is odd, the last part is a header without trailing content (we'll treat it as header with empty content).
    i = 1
    while i < len(parts):
        header_line = parts[i]
        # The content after this header is the next part, if it exists.
        content = parts[i + 1] if i + 1 < len(parts) else ""

        # Extract the header text (without the leading hashes and the space after them)
        stripped_header = header_line.strip()
        if stripped_header.startswith("#"):
            # Count the number of leading hashes
            hash_count = 0
            for ch in stripped_header:
                if ch == "#":
                    hash_count += 1
                else:
                    break
            # After the hashes, there should be a space, then the header text.
            if hash_count < len(stripped_header) and stripped_header[hash_count] == " ":
                header_text = stripped_header[hash_count + 1 :].strip()
            else:
                # Malformed header: no space after hashes. We take the rest as the header text.
                header_text = stripped_header[hash_count:].strip()
        else:
            # This should not happen because we split by the header pattern, but just in case.
            header_text = stripped_header

        # Normalize the header text for matching
        normalized_header_text = header_text.lower()

        # Replace the content with the update if available, otherwise keep original
        new_content = updates_normalized.get(normalized_header_text, content)

        # Append the header line and the (possibly updated) content
        result_parts.append(header_line)
        result_parts.append(new_content)

        # Move to the next header
        i += 2

    # Join the parts back together. Note that the split and rejoin may alter trailing newlines.
    # We join with newline to reconstruct the lines.
    return "\n".join(result_parts)


def translate_document(markdown: str, target_language: str) -> str:
    """
    Translate the entire markdown document to the target language while preserving
    markdown structure and image links.

    Args:
        markdown: The original markdown string to translate.
        target_language: The target language for translation (e.g., "Spanish", "French", "German").

    Returns:
        The translated markdown string with preserved structure and image links.

    Note:
        This function uses an LLM to perform the translation. It attempts to preserve:
        - Markdown syntax (headers, lists, code blocks, etc.)
        - Image links (![alt text](image_url)) - these are left untranslated as they reference local files
        - Code blocks (text between triple backticks)
        - Inline code (text between single backticks)
        - HTML tags (if any)
    """
    if not markdown:
        return markdown

    # If target language is English or same as source, return original
    if target_language.lower() in ["english", "en"]:
        return markdown

    # Create a translation prompt that instructs the LLM to preserve markdown structure
    # and only translate the actual content
    prompt = f"""
You are an expert technical translator. Your task is to translate the following markdown document to {target_language}
while preserving all markdown syntax, structure, and non-text elements.

IMPORTANT PRESERVATION RULES:
1. Keep ALL markdown syntax exactly as-is:
   - Headers (### Header) - translate ONLY the header text, keep the # symbols
   - Lists (- item, 1. item) - translate ONLY the item text
   - Code blocks (```code```) - DO NOT TRANSLATE, keep exactly as-is
   - Inline code (`code`) - DO NOT TRANSLATE, keep exactly as-is
   - Links [text](url) - translate ONLY the text, keep the URL as-is
   - Images ![alt text](image_url) - translate ONLY the alt text, keep the image URL as-is
   - Blockquotes (> quote) - translate ONLY the quote text
   - Horizontal rules (---) - keep exactly as-is
   - Tables - translate ONLY the cell content, keep table structure

2. DO NOT translate:
   - URLs in links or images
   - File paths in image references (like assets/{{job_id}}/step_000.png)
   - Technical terms that are commonly kept in English (use your judgment)
   - Any content inside code blocks or inline code markers

3. DO translate:
   - Header text
   - List item text
   - Paragraph text
   - Blockquote text
   - Link text (the clickable part)
   - Image alt text
   - Table cell content
   - Callout blocks (> 💡 Tip:, > ⚠️ Warning:, > 📌 Note:)

Return ONLY the translated markdown document. Do not add any explanations or extra text.

Markdown document to translate:
{markdown}
"""

    try:
        # Use the primary Llama model for translation with moderate temperature
        translated = ollama_generate_text(
            prompt=prompt,
            temperature=0.3,  # Low temperature for more consistent translation
            max_tokens=4000,  # Limit response size
        )
        return translated.strip()
    except Exception:
        # In case of failure, return the original markdown
        # In a production system, you might want to log this error
        return markdown


def extract_recapture_step_index(message: str) -> int | None:
    """
    Extract the step index from a user's chat message if it contains a recapture signal.
    Looks for patterns like:
      - "recapture step 3"
      - "retake screenshot for step 5"
      - "reshoot step 2"
      - "replace screenshot of step 7"
      - "recapture step 10"
      - etc.

    The function returns the step index as an integer (0-based or 1-based?).
    In the context of the application, the step index in the state is 0-based (as seen in the state definition:
        screenshot_assets: dict[int, str]  # step_index -> file_path
    and in the format_screenshot_markdown function, they use step_index as 0-based.

    However, the user might refer to steps as 1-based (first step, second step, etc.).
    We'll assume the user uses 1-based indexing and convert to 0-based for internal use.

    If multiple numbers are found, we take the first one that seems to be a step reference.
    If no step index is found, return None.

    Args:
        message: The user's chat message.

    Returns:
        The step index (0-based) to recapture, or None if no recapture signal or step index found.
    """
    # Convert to lowercase for case-insensitive matching
    msg_lower = message.lower()

    # List of recapture trigger keywords
    recapture_keywords = [
        "recapture",
        "retake",
        "reshoot",
        "retake screenshot",
        "retake image",
        "replace screenshot",
        "update screenshot",
        "change screenshot",
        "retake picture",
        "reshoot image",
        "capture again",
        "screenshot again",
    ]

    # Check if the message contains any recapture keyword
    if not any(keyword in msg_lower for keyword in recapture_keywords):
        return None

    # Regular expression to find a step number after a recapture keyword or near the word "step"
    # We look for patterns like:
    #   recapture step 5
    #   retake screenshot for step 3
    #   reshoot step 2
    #   replace screenshot of step 7
    #   step 5 recapture
    #   etc.

    # We'll look for the word "step" followed by a number, or a number followed by the word "step"
    # Also, we can look for the pattern where the number is near recapture keywords.

    # First, try to find a pattern: step <number>
    step_pattern = r"step\s+(\d+)"
    match = re.search(step_pattern, msg_lower)
    if match:
        step_number = int(match.group(1))
        # Convert to 0-based index (assuming user input is 1-based)
        return step_number - 1

    # If not found, try to find a pattern: <number> step
    step_pattern2 = r"(\d+)\s+step"
    match = re.search(step_pattern2, msg_lower)
    if match:
        step_number = int(match.group(1))
        return step_number - 1

    # If still not found, look for any number in the message (as a fallback)
    # But we want to be careful: we don't want to return a number that is not a step.
    # We'll look for numbers that are not part of other things (like version numbers, etc.)
    # For simplicity, we'll just look for the first number and assume it's the step.
    # This is a heuristic and might not be perfect.
    numbers = re.findall(r"\b\d+\b", msg_lower)
    if numbers:
        # Take the first number
        step_number = int(numbers[0])
        # Assume 1-based and convert to 0-based
        return step_number - 1

    # If we still haven't found a number, return None
    return None
