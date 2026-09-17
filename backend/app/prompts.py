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
