"""
LLM configuration and utility functions for DocuAgent AI.
Provides configured clients for Ollama LLM inference with JSON support.
Supports both asynchronous (httpx.AsyncClient) and synchronous (httpx.Client) execution.
"""

import json
import re
from typing import Any

import httpx

from app.config import settings


def get_ollama_analyzer_url() -> str:
    """Get the Ollama API endpoint for the analyzer model (Qwen 2.5 72B)."""
    return f"{settings.ollama_base_url}/api/generate"


def get_ollama_primary_url() -> str:
    """Get the Ollama API endpoint for the primary model (Llama 3.3 70B)."""
    return f"{settings.ollama_base_url}/api/generate"


def get_ollama_headers() -> dict[str, str]:
    """Get HTTP headers for Ollama API requests, including Bearer auth for Cloud models."""
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if settings.ollama_api_key and settings.ollama_api_key != "your-ollama-cloud-api-key-here":
        headers["Authorization"] = f"Bearer {settings.ollama_api_key}"
    return headers


# ------------------------------------------------------------------------------
# Asynchronous LLM Inference (httpx.AsyncClient)
# ------------------------------------------------------------------------------


async def async_ollama_generate_json(
    prompt: str,
    model: str | None = None,
    temperature: float = 0.1,
    max_tokens: int | None = None,
    client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """
    Asynchronously generate a JSON response from Ollama LLM using httpx.AsyncClient.
    Prevents blocking the asyncio event loop during multi-agent LangGraph execution.
    """
    if model is None:
        model = settings.ollama_analyzer_model

    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }
    if max_tokens is not None:
        payload["options"]["num_predict"] = max_tokens

    async def _send(c: httpx.AsyncClient) -> dict[str, Any]:
        resp = await c.post(
            get_ollama_analyzer_url(),
            json=payload,
            headers=get_ollama_headers(),
            timeout=settings.ollama_timeout_seconds,
        )
        resp.raise_for_status()
        data = resp.json()
        try:
            return json.loads(data["response"])
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Failed to parse JSON from LLM response: {e}") from e

    if client is not None:
        return await _send(client)
    async with httpx.AsyncClient() as new_client:
        return await _send(new_client)


async def async_ollama_generate_json_with_retry(
    prompt: str,
    model: str | None = None,
    temperature: float = 0.1,
    max_tokens: int | None = None,
    max_retries: int = 2,
    client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """
    Asynchronously generate a JSON response with automatic retry on malformed JSON.
    """
    last_exception = None
    current_temperature = temperature
    for attempt in range(max_retries + 1):
        try:
            return await async_ollama_generate_json(
                prompt=prompt,
                model=model,
                temperature=current_temperature,
                max_tokens=max_tokens,
                client=client,
            )
        except ValueError as e:
            last_exception = e
            if attempt < max_retries:
                current_temperature = max(0.0, current_temperature - 0.1)
                continue
            raise last_exception from None
        except Exception as e:
            raise e
    raise last_exception  # pragma: no cover


async def async_ollama_generate_text(
    prompt: str,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int | None = None,
    client: httpx.AsyncClient | None = None,
) -> str:
    """
    Asynchronously generate a text response from Ollama LLM using httpx.AsyncClient.
    """
    if model is None:
        model = settings.ollama_primary_model

    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }
    if max_tokens is not None:
        payload["options"]["num_predict"] = max_tokens

    async def _send(c: httpx.AsyncClient) -> str:
        resp = await c.post(
            get_ollama_primary_url(),
            json=payload,
            headers=get_ollama_headers(),
            timeout=settings.ollama_timeout_seconds,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "")

    if client is not None:
        return await _send(client)
    async with httpx.AsyncClient() as new_client:
        return await _send(new_client)


# ------------------------------------------------------------------------------
# Synchronous LLM Inference (httpx.Client)
# ------------------------------------------------------------------------------


def ollama_generate_json(
    prompt: str,
    model: str | None = None,
    temperature: float = 0.1,
    max_tokens: int | None = None,
) -> dict[str, Any]:
    """
    Generate a JSON response from Ollama LLM synchronously using httpx.Client.
    """
    if model is None:
        model = settings.ollama_analyzer_model

    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }
    if max_tokens is not None:
        payload["options"]["num_predict"] = max_tokens

    with httpx.Client(timeout=settings.ollama_timeout_seconds) as client:
        response = client.post(
            get_ollama_analyzer_url(),
            json=payload,
            headers=get_ollama_headers(),
        )
        response.raise_for_status()

    result = response.json()
    try:
        return json.loads(result["response"])
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(f"Failed to parse JSON from LLM response: {e}") from e


def ollama_generate_json_with_retry(
    prompt: str,
    model: str | None = None,
    temperature: float = 0.1,
    max_tokens: int | None = None,
    max_retries: int = 2,
) -> dict[str, Any]:
    """
    Generate a JSON response from Ollama LLM with automatic retry on malformed JSON.
    """
    last_exception = None
    current_temperature = temperature
    for attempt in range(max_retries + 1):
        try:
            return ollama_generate_json(
                prompt=prompt,
                model=model,
                temperature=current_temperature,
                max_tokens=max_tokens,
            )
        except ValueError as e:
            last_exception = e
            if attempt < max_retries:
                current_temperature = max(0.0, current_temperature - 0.1)
                continue
            raise last_exception from None
        except Exception as e:
            raise e
    raise last_exception  # pragma: no cover


def ollama_generate_text(
    prompt: str,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int | None = None,
) -> str:
    """
    Generate a text response from Ollama LLM (non-JSON) synchronously using httpx.Client.
    """
    if model is None:
        model = settings.ollama_primary_model

    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }
    if max_tokens is not None:
        payload["options"]["num_predict"] = max_tokens

    with httpx.Client(timeout=settings.ollama_timeout_seconds) as client:
        response = client.post(
            get_ollama_primary_url(),
            json=payload,
            headers=get_ollama_headers(),
        )
        response.raise_for_status()

    result = response.json()
    return result.get("response", "")


# Domain classification logic
ECOMMERCE_DOMAIN = "e-commerce"
CRM_DOMAIN = "crm"
SAAS_DOMAIN = "saas"
ADMIN_PORTAL_DOMAIN = "admin portal"
FINANCE_DOMAIN = "finance"

KNOWN_DOMAINS = {
    ECOMMERCE_DOMAIN,
    CRM_DOMAIN,
    SAAS_DOMAIN,
    ADMIN_PORTAL_DOMAIN,
    FINANCE_DOMAIN,
}

# Simple keyword mapping for domain classification
DOMAIN_KEYWORDS = {
    ECOMMERCE_DOMAIN: [
        "shop",
        "store",
        "cart",
        "checkout",
        "product",
        "inventory",
        "order",
        "payment",
        "ecommerce",
        "e-commerce",
        "retail",
        "marketplace",
    ],
    CRM_DOMAIN: [
        "crm",
        "customer relationship",
        "lead",
        "pipeline",
        "contact",
        "account",
        "salesforce",
        "hubspot",
        "zoho",
        "deal",
        "opportunity",
    ],
    SAAS_DOMAIN: [
        "saas",
        "software as a service",
        "subscription",
        "billing",
        "dashboard",
        "application",
        "platform",
        "service",
        "tenant",
    ],
    ADMIN_PORTAL_DOMAIN: [
        "admin",
        "administrator",
        "control panel",
        "dashboard",
        "settings",
        "configuration",
        "manage",
        "backend",
        "cms",
    ],
    FINANCE_DOMAIN: [
        "finance",
        "banking",
        "bank",
        "loan",
        "mortgage",
        "investment",
        "stock",
        "trading",
        "wallet",
        "payment",
        "invoice",
        "billing",
        "accounting",
    ],
}


def classify_domain(target_url: str, raw_input_script: str) -> str:
    """
    Classify the domain of the target application based on URL and script.

    Args:
        target_url: The target URL for the workflow
        raw_input_script: The natural language workflow script

    Returns:
        One of the five domains: "e-commerce", "crm", "saas", "admin portal", "finance"
    """
    # Combine URL and script for analysis
    text_to_analyze = f"{target_url} {raw_input_script}".lower()

    # Count matches for each domain
    domain_scores = dict.fromkeys(KNOWN_DOMAINS, 0)

    for domain, keywords in DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            # Use word boundaries to avoid partial matches
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, text_to_analyze):
                domain_scores[domain] += 1

    # Find the domain with the highest score
    if max(domain_scores.values()) == 0:
        # Default to saas if no keywords found
        return SAAS_DOMAIN

    return max(domain_scores, key=domain_scores.get)


def generate_selector_fallbacks(primary_selector: str, domain: str = "") -> list[str]:
    """
    Generate 2-3 fallback selectors for a given primary selector using simple heuristics.

    Args:
        primary_selector: The primary CSS/XPath selector.
        domain: The domain context (e.g., "e-commerce", "crm") - currently unused but kept for future.

    Returns:
        A list of 2-3 fallback selectors (alternatives to the primary selector),
        ordered by preference (the first being the most reliable).
    """
    alternatives = []

    # Handle ID selectors
    if primary_selector.startswith("#") and len(primary_selector) > 1:
        id_value = primary_selector[1:]
        # Attribute selector for ID
        attr_select = f'[id="{id_value}"]'
        if attr_select != primary_selector:
            alternatives.append(attr_select)
        # Wildcard with ID (less specific but still useful)
        wildcard_select = f"*#{id_value}"
        if wildcard_select != primary_selector and wildcard_select not in alternatives:
            alternatives.append(wildcard_select)
        # Try to find a name attribute with the same value (common in forms)
        name_select = f'[name="{id_value}"]'
        if name_select != primary_selector and name_select not in alternatives:
            alternatives.append(name_select)

    # Handle class selectors
    elif primary_selector.startswith(".") and len(primary_selector) > 1:
        class_value = primary_selector[1:]
        # Attribute selector for class
        attr_select = f'[class="{class_value}"]'
        if attr_select != primary_selector:
            alternatives.append(attr_select)
        # Wildcard with class
        wildcard_select = f"*.{class_value}"
        if wildcard_select != primary_selector and wildcard_select not in alternatives:
            alternatives.append(wildcard_select)
        # Try to find by class containing (though we don't have the HTML, we guess)
        contains_select = f'[class*="{class_value}"]'
        if contains_select != primary_selector and contains_select not in alternatives:
            alternatives.append(contains_select)

    # Handle attribute selectors
    elif primary_selector.startswith("[") and primary_selector.endswith("]"):
        # For attribute selectors, we can try to generalize by removing the value
        # or changing the attribute to a more common one (like id, name, class)
        # But without knowing the attribute, we do simple fallbacks
        alternatives.append("*")
        alternatives.append("body")
        # Try to guess if it's an id or name attribute
        if "id=" in primary_selector:
            alternatives.append("[id]")
        elif "name=" in primary_selector:
            alternatives.append("[name]")
        elif "class=" in primary_selector:
            alternatives.append("[class]")

    # Handle tag selectors and other selectors
    else:
        # For tag selectors, we can try to add an ID or class if we can guess (but we can't)
        # So we fall back to generic selectors
        alternatives.append("*")
        alternatives.append("body")
        alternatives.append("html")

    # Remove duplicates while preserving order
    seen = set()
    unique_alternatives = []
    for alt in alternatives:
        if alt not in seen:
            seen.add(alt)
            unique_alternatives.append(alt)

    # Ensure we have at least 2 alternatives, but no more than 3
    if len(unique_alternatives) < 2:
        # Add generic fallbacks until we have at least 2
        generic_fallbacks = ["*", "body", "html", "[id]", "[name]", "[class]"]
        for g in generic_fallbacks:
            if g not in unique_alternatives and len(unique_alternatives) < 3:
                unique_alternatives.append(g)
    # If we have more than 3, trim to 3
    if len(unique_alternatives) > 3:
        unique_alternatives = unique_alternatives[:3]

    return unique_alternatives
