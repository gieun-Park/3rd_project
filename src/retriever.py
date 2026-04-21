"""Restaurant 후보 재랭킹(Retriever).

DB/커넥터가 넘겨준 restaurant_list 를 질문과의 키워드 매칭 기반으로
top-k 개로 간단히 다시 추린다. 벡터 재정렬이 붙기 전의 기본 리트리버.
"""
from __future__ import annotations

from typing import Any


def simple_retrieve_restaurants(
    query: str,
    docs: list[dict[str, Any]],
    k: int = 3,
) -> list[dict[str, Any]]:
    """
    DB connector가 넘겨준 restaurant_list 안에서
    질문과의 단순 키워드 매칭 기반으로 top-k 후보를 다시 추린다.

    - query 토큰이 문서 전체 텍스트에 등장하면 가점
    - 문서 핵심 키워드(category/tags/menu/review tags)가 query에 부분문자열로 등장하면 큰 가점
    - 점수가 전부 0이면 앞에서 k개 fallback
    """
    if not docs:
        return []

    q = (query or "").lower()
    for ch in [".", ",", "?", "!", "~", "'", '"']:
        q = q.replace(ch, " ")
    q_tokens = [t for t in q.split() if len(t) >= 2]

    scored: list[tuple[int, dict[str, Any]]] = []

    for r in docs:
        if not isinstance(r, dict):
            continue

        doc_keywords: list[str] = []
        doc_keywords += [str(c).lower() for c in r.get("category", []) if c]
        doc_keywords += [str(t).lower() for t in r.get("tags", []) if t]
        doc_keywords += [
            str(m.get("name", "")).lower()
            for m in r.get("menus", [])
            if isinstance(m, dict)
        ]

        for rv in r.get("reviews", []):
            if isinstance(rv, dict):
                doc_keywords += [str(t).lower() for t in rv.get("tags", []) if t]

        doc_keywords = [kw for kw in doc_keywords if len(kw) >= 2]

        text_fields = [
            str(r.get("name", "")),
            str(r.get("region", "")),
            str(r.get("address", "")),
            " ".join(map(str, r.get("category", []))),
            " ".join(map(str, r.get("tags", []))),
            " ".join(
                [
                    f"{m.get('name', '')} {m.get('description', '')}"
                    for m in r.get("menus", [])
                    if isinstance(m, dict)
                ]
            ),
            " ".join(
                [
                    str(rv.get("content", ""))
                    for rv in r.get("reviews", [])
                    if isinstance(rv, dict)
                ]
            ),
        ]
        merged = " ".join(text_fields).lower()

        score = 0

        for token in q_tokens:
            if token in merged:
                score += 2

        for kw in set(doc_keywords):
            if kw in q:
                score += 3

        scored.append((score, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_docs = [item[1] for item in scored[:k] if item[0] > 0]

    return top_docs if top_docs else docs[:k]
