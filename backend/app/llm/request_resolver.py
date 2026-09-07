from __future__ import annotations

import logging
import re
from typing import Any, Literal

from pydantic import BaseModel


logger = logging.getLogger(__name__)


class RequestContext(BaseModel):
    intent: Literal[
        "general_question",
        "search_document",
        "send_document",
        "follow_up",
    ] = "general_question"

    current_query: str

    document_query: str | None = None

    is_follow_up: bool = False

    needs_document: bool = False

    needs_email: bool = False


REQUEST_RESOLVER_SYSTEM_PROMPT = """
You are a request resolver for a document-aware chatbot.

Your job is to understand ONLY the CURRENT user request.

IMPORTANT RULES:

1. The current user message ALWAYS has priority over previous messages.

2. Previous conversation may ONLY be used to resolve references such as:
   - it
   - that
   - that document
   - the previous one
   - send it
   - email it

3. If the current message explicitly names a document or document type,
   DO NOT inherit a document from previous conversation.

4. Never allow an older document request to override a newer request.

5. Never invent document IDs.

6. For document requests, document_query must contain ONLY the
   document currently requested.

7. Example:

Previous:
"Send me the branch list."

Current:
"Send me the company profile."

Correct:
{
    "document_query": "company profile"
}

Incorrect:
{
    "document_query": "branch list company profile"
}

8. For:

Previous:
"Show me the company profile."

Current:
"Send it to my email."

Correct:
{
    "intent": "follow_up",
    "current_query": "Send it to my email.",
    "document_query": "company profile",
    "is_follow_up": true,
    "needs_document": true,
    "needs_email": true
}

9. Return ONLY valid JSON.

The JSON must have exactly these fields:

{
    "intent": "general_question|search_document|send_document|follow_up",
    "current_query": "...",
    "document_query": null,
    "is_follow_up": false,
    "needs_document": false,
    "needs_email": false
}
"""


def _extract_json(raw: str) -> str:
    """
    Extract a JSON object from the LLM response.

    Handles:
    - normal JSON
    - ```json ... ```
    - ``` ... ```
    - explanatory text before/after JSON
    """

    if not raw:
        raise ValueError(
            "LLM returned an empty response."
        )

    cleaned = raw.strip()

    # Remove markdown code fences.
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines:
            first_line = lines[0].strip().lower()

            if first_line in {
                "```",
                "```json",
            }:
                lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    # Find JSON object.
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            "LLM did not return a JSON object.\n"
            f"Raw response: {raw}"
        )

    return cleaned[start:end + 1]


def _parse_json(raw: str) -> dict[str, Any]:
    """
    Safely parse JSON returned by the LLM.
    """

    json_text = _extract_json(raw)

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Failed to parse LLM JSON response.\n"
            f"JSON error: {exc}\n"
            f"Raw response: {raw}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "LLM JSON response must be an object."
        )

    return data


async def resolve_request(
    *,
    current_message: str,
    history: list[dict[str, str]] | None = None,
) -> RequestContext:

    if not current_message or not current_message.strip():
        raise ValueError(
            "Current message cannot be empty."
        )

    message = current_message.strip()
    lowered = message.lower()
    recent_history = (history or [])[-6:]
    previous_user_message = next(
        (
            item.get("content", "").strip()
            for item in reversed(recent_history)
            if item.get("role") == "user" and item.get("content", "").strip()
        ),
        None,
    )

    email_request = bool(
        re.search(r"\b(email|e-mail|mail)\b", lowered)
    )
    document_request = bool(
        re.search(
            r"\b(document|file|pdf|report|profile|list|manual|policy|terms)\b",
            lowered,
        )
    )
    follow_up = bool(
        previous_user_message
        and re.search(r"\b(it|that|this|previous|same)\b", lowered)
    )

    document_query = (
        previous_user_message
        if follow_up and not document_request
        else message
    )
    needs_document = document_request or follow_up or not email_request

    if email_request:
        intent = "follow_up" if follow_up else "send_document"
    elif document_request or follow_up:
        intent = "search_document"
    else:
        intent = "general_question"

    context = RequestContext(
        intent=intent,
        current_query=message,
        document_query=document_query if needs_document else None,
        is_follow_up=follow_up,
        needs_document=needs_document,
        needs_email=email_request,
    )

    logger.debug("Resolved request context locally: %s", context.model_dump())
    return context