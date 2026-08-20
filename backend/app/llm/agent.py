from langchain_classic.agents import (
    AgentExecutor,
    create_openai_tools_agent,
)

from app.llm.llm import get_llm
from app.rag.generation.prompts.agent_prompt import AGENT_PROMPT


def build_agent(tools: list) -> AgentExecutor:
   
    if tools is None:
        tools = []
   
    llm = get_llm()

    agent = create_openai_tools_agent(
        llm=llm,
        tools=tools,
        prompt=AGENT_PROMPT,
    )

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True,
        return_intermediate_steps=False,
    )