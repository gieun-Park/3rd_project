"""슬롯 추출(Slot Extractor).

사용자 입력 문장에서 {restaurant, menu, user} 슬롯을 추출한다.
두 라우트(`embedding` / `fixed`) 가 있으며, 프롬프트와 JSON schema name만 다르고
클라이언트/파싱 로직은 동일하므로 한 파일에서 관리한다.

- `embedding_slot_extract` (@tool): 분위기/취향 중심 검색 경로의 슬롯 추출
- `fixed_search`            (@tool): 엔티티 직접 지칭 검색 경로의 슬롯 추출
"""
from __future__ import annotations

import json
from typing import Dict

from langchain_core.tools import tool

from .config import SETTINGS
from .llm_client import get_openai_client
from .prompts import EMBEDDING_SLOT_PROMPT, FIXED_SEARCH_PROMPT


DEFAULT_FIXED_SEARCH_MODEL = SETTINGS.fixed_search_model


def _parse_slot_json(raw_json: str) -> Dict[str, str]:
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 실패: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("모델 응답이 JSON object가 아닙니다.")

    restaurant = data.get("restaurant", "") or ""
    menu = data.get("menu", "") or ""
    user = data.get("user", "") or ""

    if not isinstance(restaurant, str) or not isinstance(menu, str) or not isinstance(user, str):
        raise ValueError("restaurant, menu, user 값은 문자열이어야 합니다.")

    return {
        "restaurant": restaurant.strip(),
        "menu": menu.strip(),
        "user": user.strip(),
    }


def _make_embedding_slot_json(
    instr: str,
    model: str | None = None,
) -> str:
    model = model or SETTINGS.fixed_search_model

    completion = get_openai_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "developer", "content": EMBEDDING_SLOT_PROMPT},
            {"role": "user", "content": instr},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "embedding_slot_result",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "restaurant": {"type": "string"},
                        "menu": {"type": "string"},
                        "user": {"type": "string"},
                    },
                    "required": ["restaurant", "menu", "user"],
                    "additionalProperties": False,
                },
            },
        },
        temperature=0,
        max_completion_tokens=120,
        top_p=1,
    )

    content = completion.choices[0].message.content
    if not content:
        raise ValueError("모델이 빈 응답을 반환했습니다.")
    return content


def _make_fixed_search_json(instr: str, model: str = DEFAULT_FIXED_SEARCH_MODEL) -> str:
    completion = get_openai_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "developer", "content": FIXED_SEARCH_PROMPT},
            {"role": "user", "content": instr},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "fixed_search_result",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "restaurant": {"type": "string"},
                        "menu": {"type": "string"},
                        "user": {"type": "string"},
                    },
                    "required": ["restaurant", "menu", "user"],
                    "additionalProperties": False,
                },
            },
        },
        temperature=0,
        max_completion_tokens=120,
        top_p=1,
    )

    content = completion.choices[0].message.content
    if not content:
        raise ValueError("모델이 빈 응답을 반환했습니다.")
    return content


@tool("embedding_slot_extract")
def embedding_slot_extract(instr: str) -> Dict[str, str]:
    """
    사용자 입력을 restaurant/menu/user 슬롯 구조로 1차 반환한다.

    Returns:
        {"restaurant": "...", "menu": "...", "user": "..."}
    """
    instr = (instr or "").strip()
    if not instr:
        return {"restaurant": "", "menu": "", "user": ""}

    raw_json = _make_embedding_slot_json(instr)
    return _parse_slot_json(raw_json)


@tool("fixed_search")
def fixed_search(instr: str) -> Dict[str, str]:
    """
    사용자 검색 문장을 restaurant/menu/user 슬롯으로 분류해 반환한다.
    """
    instr = (instr or "").strip()
    if not instr:
        return {"restaurant": "", "menu": "", "user": ""}

    raw_json = _make_fixed_search_json(instr)
    return _parse_slot_json(raw_json)


if __name__ == "__main__":
    test_input = "초밥천사 집에 우동 팔아?"
    print("[embedding]", embedding_slot_extract.invoke(test_input))

    test_input2 = "신대방삼거리 근처 곱창전골 맛집"
    print("[fixed]", fixed_search.invoke(test_input2))
