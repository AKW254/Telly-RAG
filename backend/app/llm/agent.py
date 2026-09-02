
from __future__ import annotations

from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)

from langchain_classic.agents import (
    AgentExecutor,
    create_openai_tools_agent,
)

from app.llm.llm import get_llm
from app.config.settings import settings


DOCUMENT_AGENT_SYSTEM_PROMPT = """
You are a document assistant.

You operate ONLY on the current request.

You receive:

CURRENT REQUEST
REQUEST CONTEXT
RETRIEVED DOCUMENT CONTEXT
USER CONTEXT

IMPORTANT RULES:

1. The CURRENT REQUEST has priority.

2. There is NO conversation history available to you.

3. Never use an old document from a previous conversation.

4. request_context is the authoritative interpretation of the
   current request.

5. Retrieved documents are specific to the current request.

6. Never invent document IDs.

7. Only use document IDs present in retrieved document context
   or returned by find_document.

8. If the user requests a different document from an earlier request,
   use the new document.

9. Do not assume that the previously discussed document is still active.

10. For email requests, first identify the correct document and then
    use the email tool.
"""


def build_agent(
    *,
    tools: list,
    system_prompt: str = DOCUMENT_AGENT_SYSTEM_PROMPT,
) -> AgentExecutor:

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            (
                "human",
                """
CURRENT REQUEST:
{input}

REQUEST CONTEXT:
{request_context}

RETRIEVED DOCUMENT CONTEXT:
{context}

USER CONTEXT:
{user_context}
""",
            ),
            MessagesPlaceholder(
                "agent_scratchpad"
            ),
        ]
    )

    agent = create_openai_tools_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=settings.debug,
        max_iterations=10,
        handle_parsing_errors=True,
        return_intermediate_steps=False,
    )