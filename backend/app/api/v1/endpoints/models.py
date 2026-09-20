"""
Ollama Model Management & Discovery Endpoint for DocuAgent AI.
"""

import httpx
from fastapi import APIRouter

from app.config import settings
from app.llm import get_ollama_headers

router = APIRouter(tags=["models"])

DEFAULT_MODELS = [
    "llama3.3:70b",
    "llama3.1:8b",
    "qwen2.5:72b",
    "qwen2.5:32b",
    "qwen2.5:7b",
    "mistral-large",
    "deepseek-r1:70b",
]


@router.get("/models")
async def list_available_models():
    """
    Fetch available models from the configured Ollama endpoint (local or cloud).
    Falls back to configured/default models if the endpoint is temporarily unreachable.
    """
    url = f"{settings.ollama_base_url}/api/tags"
    discovered: list[str] = []
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url, headers=get_ollama_headers())
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("models", []):
                    name = item.get("name")
                    if name and name not in discovered:
                        discovered.append(name)
    except Exception:
        pass

    all_models = list(discovered) if discovered else list(DEFAULT_MODELS)

    # Ensure configured primary and analyzer models are present in the options
    if settings.ollama_primary_model not in all_models:
        all_models.insert(0, settings.ollama_primary_model)
    if (
        settings.ollama_analyzer_model not in all_models
        and settings.ollama_analyzer_model != settings.ollama_primary_model
    ):
        all_models.append(settings.ollama_analyzer_model)

    return {
        "models": all_models,
        "default_primary": settings.ollama_primary_model,
        "default_analyzer": settings.ollama_analyzer_model,
        "is_live": len(discovered) > 0,
    }
