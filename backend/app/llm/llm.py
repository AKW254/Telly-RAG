from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openrouter import ChatOpenRouter

from app.config.settings import settings


@lru_cache
def get_llm() -> BaseChatModel:
    """
    Create the application's OpenRouter chat model.

    This is the single LLM configuration used by
    generation and agent components.
    """

    api_key = (
        settings.openrouter_api_key

    )

    if not api_key:
        raise RuntimeError(
            "OpenRouter API key is not configured."
        )

    return ChatOpenRouter(
        model=settings.openrouter_model_name,
        api_key=api_key,
        base_url=settings.openrouter_base_url,
        temperature=getattr(
            settings,
            "llm_temperature",
            0.2,
        ),
        max_tokens=getattr(
            settings,
            "llm_max_tokens",
            2048,
        ),
    )