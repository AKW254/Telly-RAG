# app/llm/request_resolver.py

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm.llm import get_llm


class RequestContext(BaseModel):
    intent: str = "general_question"
    current_query: str
    document_query: str | None = None

    is_follow_up: bool = False
    needs_document: bool = False
    needs_email: bool = False


REQUEST_RESOLVER_SYSTEM_PROMPT = """
You are a request resolver for a document-aware chatbot.

Your job is to understand the CURRENT user request.

IMPORTANT:

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

6. For document requests, document_query must contain ONLY the document
   currently requested.

7. For example:

Previous:
"Send me the branch list."

Current:
"Send me the company profile."

Correct:
document_query = "company profile"

NOT:
document_query = "branch list company profile"

8. For:

Previous:
"Show me the company profile."

Current:
"Send it to my email."

Correct:
document_query = "company profile"
is_follow_up = true
needs_document = true
needs_email = true

Return ONLY valid JSON:

{
    "intent": "general_question|search_document|send_document|follow_up",
    "current_query": "...",
    "document_query": null,
    "is_follow_up": false,
    "needs_document": false,
    "needs_email": false
}
"""


def _parse_json(raw: str) -> dict[str, Any]:
    cleaned = raw.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")

        if cleaned.startswith("json"):
            cleaned = cleaned[4:]

        cleaned = cleaned.strip()

    return json.loads(cleaned)


async def resolve_request(
    *,
    current_message: str,
    history: list[dict[str, str]] | None = None,
) -> RequestContext:

    # Only recent conversation is exposed to the resolver.
    recent_history = (history or [])[-6:]

    prompt = f"""
CURRENT USER REQUEST:
{current_message}

RECENT CONVERSATION:
{json.dumps(recent_history, ensure_ascii=False)}
"""

    llm = get_llm()

    response = await llm.ainvoke(
        [
            SystemMessage(content=REQUEST_RESOLVER_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    return RequestContext.model_validate(
        _parse_json(response.content)
    )