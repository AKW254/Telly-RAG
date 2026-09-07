import asyncio
import logging
from functools import lru_cache
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openrouter import ChatOpenRouter

from app.config.settings import settings


logger = logging.getLogger(__name__)


@lru_cache
def get_llm(model_name: str | None = None) -> BaseChatModel:
    api_key = settings.openrouter_api_key

    if not api_key:
        raise RuntimeError("OpenRouter API key is not configured.")

    return ChatOpenRouter(
        model=model_name or settings.openrouter_model_name,
        api_key=api_key,
        base_url=settings.openrouter_base_url,
        temperature=getattr(settings, "llm_temperature", 0.2),
        max_tokens=getattr(settings, "llm_max_tokens", 2048),
    )


def _is_rate_limit_error(error: Exception) -> bool:
    return (
        "TooManyRequests" in type(error).__name__
        or "429" in str(error)
    )


async def invoke_llm(messages: list[Any]) -> Any:
    model_names = [settings.openrouter_model_name]
    fallback_model = settings.openrouter_fallback_model_name

    if fallback_model and fallback_model not in model_names:
        model_names.append(fallback_model)

    last_error: Exception | None = None

    for model_name in model_names:
        llm = get_llm(model_name)

        for attempt in range(3):
            try:
                return await llm.ainvoke(messages)
            except Exception as error:
                last_error = error

                if not _is_rate_limit_error(error) or attempt == 2:
                    break

                delay = 2 ** attempt
                logger.warning(
                    "LLM model %s was rate-limited; retrying in %s seconds.",
                    model_name,
                    delay,
                )
                await asyncio.sleep(delay)

    if last_error is not None:
        raise last_error

    raise RuntimeError("No LLM model is configured.")