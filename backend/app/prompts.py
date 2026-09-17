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


# Prompt for Agent 4: Quality & Verification Agent
# Evaluates the generated document for completeness, screenshot coverage, tone consistency, and logical sequencing
QUALITY_REVIEW_PROMPT = """
You are an expert quality assurance specialist and technical editor.
Your task is to evaluate a technical document for quality and provide structured feedback.

Evaluate the document based on these four criteria:

1. COMPLETENESS
   - Does the document cover all steps in the workflow?
   - Are all prerequisites listed?
   - Is the system overview comprehensive?
   - Does the step-by-step walkthrough have clear instructions for each step?
   - Does the troubleshooting section address common issues?
   - Are there any missing sections or incomplete explanations?

2. SCREENSHOT COVERAGE
   - Does each step in the workflow have a corresponding screenshot reference?
   - Are screenshot references in the correct format: ![Step X](assets/{job_id}/step_{index:03d}.png)?
   - Are all screenshots accounted for in the document?
   - Are there any extra or missing screenshot references?

3. TONE CONSISTENCY
   - Is the document written in a consistent, professional tone?
   - Is the second person perspective ("you") used consistently for instructions?
   - Is the language clear, concise, and free of jargon where possible?
   - Are callout blocks (> 💡 Tip:, > ⚠️ Warning:, > 📌 Note:) used appropriately?

4. LOGICAL SEQUENCING
   - Does the document flow logically from prerequisites to troubleshooting?
   - Are steps in the correct order?
   - Does the information build upon itself appropriately?
   - Are there any gaps or jumps in logic?

Provide your evaluation as a JSON object with the following structure:
{
  "completeness": {
    "score": 0-100,
    "feedback": "Detailed feedback on completeness issues"
  },
  "screenshot_coverage": {
    "score": 0-100,
    "feedback": "Detailed feedback on screenshot coverage issues"
  },
  "tone_consistency": {
    "score": 0-100,
    "feedback": "Detailed feedback on tone consistency issues"
  },
  "logical_sequencing": {
    "score": 0-100,
    "feedback": "Detailed feedback on logical sequencing issues"
  },
  "overall_pass": true/false,
  "summary": "Overall summary of the quality review"
}

Consider the document to pass only if all four criteria score 80 or above.
Provide specific, actionable feedback in each section.
If the document passes, still provide feedback on any minor improvements that could be made.

Workflow steps and context:
{structured_steps}
Screenshot assets: {screenshot_assets}
Domain context: {domain_context}
Raw input script: {raw_input_script}
Generated markdown content:
{markdown_content}

Remember: Output ONLY the JSON object.
"""


def format_screenshot_markdown(step_index: int, file_path: str, job_id: str = "") -> str:
    """
    Format a screenshot asset as a Markdown image tag.
    If the file_path is a placeholder indicator (starts with "PLACEHOLDER:"),
    returns a text-only placeholder tag instead.

    Args:
        step_index: The step index (0-based)
        file_path: The file path to the screenshot, or a placeholder indicator
                  starting with "PLACEHOLDER:" followed by placeholder text
        job_id: The job ID (used for validation or context, optional)

    Returns:
        A Markdown image tag string: ![Step X](file_path)
        Or a placeholder tag: [Insert Screenshot Here: placeholder_text]

    Example:
        >>> format_screenshot_markdown(0, "assets/job123/step_000.png")
        '![Step 0](assets/job123/step_000.png)'
        >>> format_screenshot_markdown(0, "PLACEHOLDER:Click login button")
        '[Insert Screenshot Here: Click login button]'
    """
    # Check if this is a placeholder indicator
    if file_path.startswith("PLACEHOLDER:"):
        # Extract the placeholder text (everything after "PLACEHOLDER:")
        placeholder_text = file_path[12:]  # Remove "PLACEHOLDER:" prefix
        return f"[Insert Screenshot Here: {placeholder_text}]"

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
