"""프로젝트 전역에서 공유되는 OpenAI 클라이언트 싱글톤.

기존 `embedding_service.py`, `llm_tool2.py`에 중복되어 있던
`_get_client()` 로직을 한곳으로 모은다.
"""
from __future__ import annotations

from openai import OpenAI

from .config import SETTINGS


_client: OpenAI | None = None


def get_openai_client() -> OpenAI:
    global _client
    if _client is None:
        if not SETTINGS.openai_api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.")
        _client = OpenAI(api_key=SETTINGS.openai_api_key)
    return _client
