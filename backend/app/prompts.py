"""
Prompt templates for DocuAgent AI agents.
"""

# Prompt for Agent 1: Script & Domain Analyzer
# Extracts actionable UI interactions into a JSON DAG of StepSchema objects
SCRIPT_ANALYSIS_PROMPT = """
You are an expert UI/UX analyst and robotic process automation specialist.
Your task is to analyze a natural language workflow script and extract a structured, ordered list of UI interaction steps.

Each step must be represented as a JSON object with the following fields:
- index: Integer, starting from 0, indicating the step order.
- description: A clear, concise description of what the step accomplishes.
- action_type: One of the following: "navigate", "click", "type", "scroll", "wait", "authenticate".
- target_selector: A CSS or XPath selector string that uniquely identifies the target UI element for the action.
- input_value: The text to be input if action_type is "type"; otherwise, an empty string.
- expected_url: The URL that the browser is expected to be on after completing this step (if known; otherwise, empty string).
- domain_context: A brief categorization of the website or application domain (e.g., "e-commerce", "saas dashboard", "banking portal").
- selector_hints: An array of 2-3 alternative selector strings (CSS/XPath) that could be used to target the same element, ordered by preference (with the first being the most reliable).

The output must be a valid JSON array of these step objects, sorted by index in ascending order.
Do not include any additional text, explanation, or formatting outside the JSON array.

Example output format:
[
  {
    "index": 0,
    "description": "Navigate to the login page",
    "action_type": "navigate",
    "target_selector": "body",
    "input_value": "",
    "expected_url": "https://example.com/login",
    "domain_context": "saas dashboard",
    "selector_hints": ["body", "html", "*"]
  },
  {
    "index": 1,
    "description": "Enter username in the username field",
    "action_type": "type",
    "target_selector": "#username",
    "input_value": "the user's username",
    "expected_url": "https://example.com/login",
    "domain_context": "saas dashboard",
    "selector_hints": ["#username", "input[name='username']", ".username-field"]
  }
]

Now, analyze the following workflow script and extract the steps:

{raw_input_script}

Remember: Output ONLY the JSON array.
"""


# Prompt for Agent 3: Technical Writer & Layout Agent
# Structures technical documentation with standard sections
COMPILE_MARKDOWN_PROMPT = """
You are an expert technical writer and documentation specialist.
Your task is to synthesize a comprehensive, well-structured technical document based on the provided workflow steps and screenshot assets.

The document MUST include the following standard sections in this order:

## Prerequisites
List any requirements, assumptions, or setup needed before executing the workflow.
Examples: software versions, account requirements, network access, initial state.

## System Overview
Provide a high-level description of the system or application being documented.
Include purpose, main components, and relevant domain context.

## Step-by-Step Walkthrough
For each step in the workflow, provide:
1. A clear description of what the step accomplishes
2. Instructions for executing the step
3. The corresponding screenshot (refer to it as ![Step X](assets/{job_id}/step_{index:03d}.png))
4. Any important notes, tips, or warnings related to this step

## Troubleshooting
Common issues that users might encounter and how to resolve them.
Include error messages, their likely causes, and step-by-step solutions.

Formatting guidelines:
- Use clear, concise language
- Write in the second person ("you") for instructions
- Include relevant details from the workflow steps and domain context
- Reference screenshots using the standard Markdown image syntax
- Format callout blocks as:
    > 💡 Tip: [tip message]
    > ⚠️ Warning: [warning message]
    > 📌 Note: [note message]
- Ensure the document flows logically from prerequisites to troubleshooting
- Do not include any additional sections or content outside the specified ones

Workflow steps and context:
{structured_steps}
Screenshot assets: {screenshot_assets}
Domain context: {domain_context}
Raw input script: {raw_input_script}
Quality feedback: {quality_feedback}

Generate ONLY the Markdown document with the four required sections.
If quality_feedback is provided, pay close attention to the feedback and address all points raised in the revised document.
"""


def format_screenshot_markdown(step_index: int, file_path: str, job_id: str = "") -> str:
    """
    Format a screenshot asset as a Markdown image tag.

    Args:
        step_index: The step index (0-based)
        file_path: The file path to the screenshot
        job_id: The job ID (used for validation or context, optional)

    Returns:
        A Markdown image tag string: ![Step X](file_path)

    Example:
        >>> format_screenshot_markdown(0, "assets/job123/step_000.png")
        '![Step 0](assets/job123/step_000.png)'
    """
    # Ensure the file_path is relative or absolute as needed
    # The screenshot_assets in ManualState should already contain the correct path
    return f"![Step {step_index}]({file_path})"


def map_screenshot_assets_to_markdown(
    screenshot_assets: dict[int, str], job_id: str = ""
) -> dict[int, str]:
    """
    Map screenshot assets dictionary to Markdown image tags.

    Args:
        screenshot_assets: Dictionary mapping step_index to file_path
        job_id: The job ID (for validation/context, optional)

    Returns:
        Dictionary mapping step_index to Markdown image tag string

    Example:
        >>> assets = {0: "assets/job123/step_000.png", 1: "assets/job123/step_001.png"}
        >>> map_screenshot_assets_to_markdown(assets)
        {0: '![Step 0](assets/job123/step_000.png)', 1: '![Step 1](assets/job123/step_001.png)'}
    """
    markdown_tags = {}
    for step_index, file_path in screenshot_assets.items():
        markdown_tags[step_index] = format_screenshot_markdown(step_index, file_path, job_id)
    return markdown_tags
