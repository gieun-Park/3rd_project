"""라우터(Router).

사용자 질문을 보고 `embedding` / `fixed` 경로 중 하나를 선택한다.
"""
from __future__ import annotations

from langchain_openai import ChatOpenAI

from .config import SETTINGS
from .prompts import ROUTER_PROMPT


def decide_route(question: str) -> str:
    llm = ChatOpenAI(
        model=SETTINGS.router_model,
        temperature=0,
        api_key=SETTINGS.openai_api_key,
    )

    raw = llm.invoke(ROUTER_PROMPT.replace("{question}", question)).content.strip().lower()
    if "fixed" in raw:
        return "fixed"
    return "embedding"
