from langchain_core.messages import HumanMessage, SystemMessage

from app.ai.gemini_client import get_llm
from app.ai.prompt_loader import get_prompt


def generate_with_prompt(prompt_name: str, user_request: str) -> str:
    system_prompt = get_prompt("system_prompt")
    selected_prompt = get_prompt(prompt_name)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=f"""Use this prompt template:
{selected_prompt}

User request:
{user_request}"""
        ),
    ]
    response = get_llm().invoke(messages)
    return getattr(response, "text", response.content)
