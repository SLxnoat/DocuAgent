"""
Backend configuration management using pydantic-settings.
"""

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application & Server Settings
    app_name: str = "DocuAgent AI"
    app_env: str = Field(default="development", env="APP_ENV")
    app_debug: bool = Field(default=True, env="APP_DEBUG")
    app_host: str = Field(default="0.0.0.0", env="APP_HOST")
    app_port: int = Field(default=8000, env="APP_PORT")
    secret_key: str = Field(
        default="change-this-to-a-cryptographically-secure-random-string-in-production",
        env="SECRET_KEY",
    )
    api_token: str = Field(default="dev-secret-token-change-in-production", env="API_TOKEN")
    allowed_origins: str | list[str] = Field(
        default="http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
        env="ALLOWED_ORIGINS",
    )

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_ttl_hours: int = Field(default=24, env="REDIS_TTL_HOURS")
    celery_broker_url: str = Field(default="redis://localhost:6379/1", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND"
    )
    redis_pubsub_url: str = Field(default="redis://localhost:6379/3", env="REDIS_PUBSUB_URL")

    # Ollama Cloud LLM Inference Configuration
    ollama_base_url: str = Field(default="https://ollama.example.com", env="OLLAMA_BASE_URL")
    ollama_api_key: str = Field(default="your-ollama-cloud-api-key-here", env="OLLAMA_API_KEY")
    ollama_primary_model: str = Field(default="llama3.3:70b", env="OLLAMA_PRIMARY_MODEL")
    ollama_analyzer_model: str = Field(default="qwen2.5:72b", env="OLLAMA_ANALYZER_MODEL")
    ollama_timeout_seconds: int = Field(default=120, env="OLLAMA_TIMEOUT_SECONDS")
    ollama_max_retries: int = Field(default=3, env="OLLAMA_MAX_RETRIES")

    # Playwright Browser Automation Engine
    playwright_browser: str = Field(default="chromium", env="PLAYWRIGHT_BROWSER")
    playwright_headless: bool = Field(default=True, env="PLAYWRIGHT_HEADLESS")
    playwright_viewport_width: int = Field(default=1440, env="PLAYWRIGHT_VIEWPORT_WIDTH")
    playwright_viewport_height: int = Field(default=900, env="PLAYWRIGHT_VIEWPORT_HEIGHT")
    playwright_selector_timeout_ms: int = Field(default=10000, env="PLAYWRIGHT_SELECTOR_TIMEOUT_MS")
    playwright_navigation_timeout_ms: int = Field(
        default=30000, env="PLAYWRIGHT_NAVIGATION_TIMEOUT_MS"
    )
    playwright_max_retries: int = Field(default=2, env="PLAYWRIGHT_MAX_RETRIES")
    playwright_highlight_color: str = Field(default="#06b6d4", env="PLAYWRIGHT_HIGHLIGHT_COLOR")
    playwright_highlight_opacity: float = Field(default=0.15, env="PLAYWRIGHT_HIGHLIGHT_OPACITY")

    # Media & Storage Paths
    assets_dir: str = Field(default="../assets", env="ASSETS_DIR")
    exports_dir: str = Field(default="../exports", env="EXPORTS_DIR")
    asset_retention_hours: int = Field(default=24, env="ASSET_RETENTION_HOURS")

    # Document Export Subsystems
    weasyprint_enabled: bool = Field(default=True, env="WEASYPRINT_ENABLED")
    pandoc_enabled: bool = Field(default=True, env="PANDOC_ENABLED")

    # Celery Worker Concurrency & Safety
    celery_worker_concurrency: int = Field(default=5, env="CELERY_WORKER_CONCURRENCY")
    celery_task_timeout_seconds: int = Field(default=600, env="CELERY_TASK_TIMEOUT_SECONDS")
    celery_max_tasks_per_child: int = Field(default=50, env="CELERY_MAX_TASKS_PER_CHILD")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    @validator("allowed_origins", pre=True)
    def split_allowed_origins(cls, v: str | list[str]) -> list[str]:  # noqa: N805
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator(
        "asset_retention_hours",
        "celery_worker_concurrency",
        "celery_task_timeout_seconds",
        "celery_max_tasks_per_child",
    )
    def positive_int(cls, v: int) -> int:  # noqa: N805
        if v <= 0:
            raise ValueError("must be positive")
        return v


settings = Settings()
