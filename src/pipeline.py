"""질의응답 파이프라인(LangGraph) + CLI 진입점.

- `run_qa(question, connector_response, session_id)` : 외부 호출용 API
- `python -m src.pipeline`                          : 터미널에서 대화 테스트
"""
from __future__ import annotations

from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from .generator import generate_response
from .mock_data import restaurant_list as MOCK_RESTAURANT_LIST
from .router import decide_route
from .slot_extractor import embedding_slot_extract, fixed_search


class GraphState(TypedDict, total=False):
    question: str
    session_id: str

    # ============================================================
    # [커넥터 반환 데이터가 들어오는 자리]
    # pipeline.main() 또는 외부 호출부에서 아래 형태로 넘겨준다고 가정
    #
    # {
    #     "restaurant_list": [...],
    #     "search_mode": "...",
    #     "candidate_count": ...
    # }
    # ============================================================
    connector_response: dict[str, Any]

    route: Literal["embedding", "fixed"]
    route_payload: dict[str, str]

    restaurant_list: list[dict[str, Any]]
    answer: str


_graph = None


def _normalize_connector_response(result: Any) -> dict[str, Any]:
    if result is None:
        return {"restaurant_list": []}

    if isinstance(result, dict):
        restaurant_list = result.get("restaurant_list", [])
        if restaurant_list is None:
            restaurant_list = []

        if not isinstance(restaurant_list, list):
            raise ValueError("connector_response['restaurant_list']는 list 형태여야 합니다.")

        return {
            **result,
            "restaurant_list": restaurant_list,
        }

    if isinstance(result, list):
        return {"restaurant_list": result}

    raise ValueError("connector_response는 dict 또는 list 형태여야 합니다.")


def route_node(state: GraphState) -> GraphState:
    return {"route": decide_route(state["question"])}


def embedding_slot_node(state: GraphState) -> GraphState:
    payload = embedding_slot_extract.invoke(state["question"])
    return {"route_payload": payload}


def fixed_slot_node(state: GraphState) -> GraphState:
    payload = fixed_search.invoke(state["question"])
    return {"route_payload": payload}


def connector_prepare_node(state: GraphState) -> GraphState:
    # ============================================================
    # [커넥터 반환 데이터 받아오는 곳]
    # 외부(main 등)에서 전달받은 connector_response를 여기서 정규화함
    # ============================================================
    connector_response = _normalize_connector_response(state.get("connector_response"))

    # ============================================================
    # [커넥터 데이터에서 restaurant_list 추출하는 곳]
    # 이후 generate_response에 들어갈 핵심 데이터
    # ============================================================
    restaurant_list = connector_response.get("restaurant_list", [])

    return {
        "connector_response": connector_response,
        "restaurant_list": restaurant_list,
    }


def generate_node(state: GraphState) -> GraphState:
    question = state["question"]
    session_id = state.get("session_id", "default")
    route = state.get("route", "embedding")
    route_payload = state.get("route_payload", {})
    restaurant_list = state.get("restaurant_list", [])
    connector_response = state.get("connector_response", {})

    connector_meta = {
        k: v
        for k, v in connector_response.items()
        if k != "restaurant_list"
    }
    connector_meta["restaurant_count"] = len(restaurant_list)

    answer = generate_response(
        question=question,
        restaurant_list=restaurant_list,
        route=route,
        session_id=session_id,
        route_payload=route_payload,
        connector_meta=connector_meta,
    )
    return {"answer": answer}


def route_condition(state: GraphState) -> str:
    return state["route"]


def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("route_node", route_node)
    graph.add_node("embedding_slot_node", embedding_slot_node)
    graph.add_node("fixed_slot_node", fixed_slot_node)
    graph.add_node("connector_prepare_node", connector_prepare_node)
    graph.add_node("generate_node", generate_node)

    graph.add_edge(START, "route_node")

    graph.add_conditional_edges(
        "route_node",
        route_condition,
        {
            "embedding": "embedding_slot_node",
            "fixed": "fixed_slot_node",
        },
    )

    graph.add_edge("embedding_slot_node", "connector_prepare_node")
    graph.add_edge("fixed_slot_node", "connector_prepare_node")

    graph.add_edge("connector_prepare_node", "generate_node")
    graph.add_edge("generate_node", END)

    return graph.compile()


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def run_qa(
    question: str,
    connector_response: dict[str, Any] | list[dict[str, Any]],
    session_id: str = "default",
) -> dict[str, Any]:
    graph = get_graph()

    # ============================================================
    # [외부에서 커넥터 반환 데이터를 주입하는 곳]
    # main()이 connector_response를 넘겨주면 여기서 그래프에 넣음
    # ============================================================
    result = graph.invoke(
        {
            "question": question,
            "session_id": session_id,
            "connector_response": connector_response,
        }
    )

    return {
        "question": question,
        "route": result.get("route"),
        "route_payload": result.get("route_payload", {}),
        "connector_response": result.get("connector_response", {}),
        "restaurant_list": result.get("restaurant_list", []),
        "answer": result.get("answer", ""),
    }


def main() -> None:
    """CLI 대화형 테스트 진입점.

    빈 Enter로 종료. 커넥터 자리에는 `mock_data.restaurant_list` 를 주입.
    """
    print("=" * 60)
    print("맛집 추천 CLI 테스트 (빈 Enter 입력시 종료)")
    print("=" * 60)

    while True:
        try:
            question = input("\n질문 > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다.")
            break

        if not question:
            print("종료합니다.")
            break

        connector_response = {
            "restaurant_list": MOCK_RESTAURANT_LIST,
            "search_mode": "embedding",
            "candidate_count": len(MOCK_RESTAURANT_LIST),
        }

        result = run_qa(
            question=question,
            connector_response=connector_response,
            session_id="default",
        )

        # print(f"\n[route]   {result.get('route')}")
        # print(f"[payload] {result.get('route_payload')}")
        print("\n[답변]")
        print(result["answer"])


if __name__ == "__main__":
    main()
