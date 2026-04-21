# `src/` 리팩터링 설계 문서

작성일: 2026-04-21
대상: `c:/MinHyeok/skn26_3rd_3rd/3rd_project/src/`

---

## 1. 현재 구조 진단

### 1.1 파일 현황
| 파일 | 주요 내용 |
|---|---|
| `config.py` | `Settings` dataclass, 환경변수 로드 |
| `embeddings.py` | `OpenAIEmbeddings` 래퍼 (`get_embedding_model`, `embed_query`, `embed_documents`) |
| `embedding_service.py` | `EMBEDDING_SLOT_PROMPT`, `_make_embedding_slot_json`, `EmbeddingSearchService.extract_slots`, 내부 OpenAI 클라이언트 |
| `embedding_tool.py` | `@tool embedding_slot_extract` (얇은 래퍼) |
| `llm_tool2.py` | `FIXED_SEARCH` 프롬프트, `_make_fixed_search_json`, `_parse_fixed_search_json`, `@tool fixed_search`, 내부 OpenAI 클라이언트 |
| `generate.py` | `load_prompt_template`, 세션 히스토리, `get_llm`, `simple_retrieve_restaurants`, `generate_response` |
| `pipeline.py` | 라우터 프롬프트 + `decide_route` + 그래프 노드 + `run_qa` |
| `main.py` | CLI 진입점. `test_mockupdata`(존재 X) 임포트. |

### 1.2 문제점
1. **OpenAI 클라이언트 중복**: `embedding_service.py`와 `llm_tool2.py`에 거의 동일한 `_get_client()` 가 별도로 존재.
2. **프롬프트 산재**: 슬롯 추출 프롬프트 2개 + 라우터 프롬프트가 서로 다른 파일에 인라인으로 박혀 있음.
3. **모호한 네이밍**: `llm_tool2.py`는 역할을 드러내지 못함. `embedding_service.py`와 `embedding_tool.py`가 기능적으로 거의 같은 층(슬롯 추출)임.
4. **순환스러운 교차 임포트**: `embedding_service.py` → `llm_tool2.py._parse_fixed_search_json` 을 가져다 씀. 이름상 "embedding"이 "fixed"에 의존하는 형태라 읽기 어려움.
5. **혼합된 책임**: `generate.py`에 프롬프트 로드 / 문서 재랭킹(`simple_retrieve_restaurants`) / LLM 호출이 한 파일에 섞여 있음.
6. **CLI 가 깨져있음**: `src/main.py`가 존재하지 않는 `test_mockupdata`를 임포트하므로 실제 실행이 불가.

---

## 2. 리팩터링 원칙

- **함수 본체/로직은 그대로 유지**. 파일 이동·이름변경 위주.
- **책임 단위로 파일을 분리** (Single Responsibility).
- **중복 제거**(OpenAI 클라이언트, 파싱 함수) 만 함수 시그니처 수준에서 허용.
- **CLI가 곧바로 동작**하도록 최소한의 mock 데이터 포함.

---

## 3. 목표 구조

```
src/
├── __init__.py              # (유지)
├── config.py                # (유지) 환경설정
├── prompts.py               # (신규) 프롬프트 상수 집중
├── llm_client.py            # (신규) OpenAI 클라이언트 싱글톤
├── embeddings.py            # (유지) OpenAIEmbeddings 래퍼
├── slot_extractor.py        # (신규) 슬롯 추출 통합 (embedding/fixed)
├── retriever.py             # (신규) restaurant 재랭킹
├── generator.py             # (신규, generate.py 리네임) 최종 응답 생성
├── router.py                # (신규) embedding vs fixed 라우팅 판정
├── pipeline.py              # (수정) 그래프 + CLI main()
└── mock_data.py             # (신규) CLI 테스트용 샘플 restaurant_list
```

### 3.1 삭제되는 파일
- `src/main.py` → 내용 `pipeline.py`로 이동
- `src/embedding_service.py` → `slot_extractor.py`로 흡수
- `src/embedding_tool.py` → `slot_extractor.py`로 흡수
- `src/llm_tool2.py` → `slot_extractor.py`로 흡수
- `src/generate.py` → `generator.py` + `retriever.py` 로 분할

---

## 4. 파일별 매핑 (어느 함수/상수가 어디로 가는가)

### 4.1 `prompts.py` (신규)
| 원본 | → 이동 후 |
|---|---|
| `embedding_service.py::EMBEDDING_SLOT_PROMPT` | `prompts.EMBEDDING_SLOT_PROMPT` |
| `llm_tool2.py::prompt` (이름 모호) | `prompts.FIXED_SEARCH_PROMPT` |
| `pipeline.py::decide_route` 내 인라인 `router_prompt` | `prompts.ROUTER_PROMPT` |
| `generate.py::load_prompt_template` | `prompts.load_system_prompt` (이름만 변경) |

### 4.2 `llm_client.py` (신규)
| 원본 | → 이동 후 |
|---|---|
| `embedding_service.py::_get_client` (중복) | `llm_client.get_openai_client` (통합) |
| `llm_tool2.py::_get_client` (중복) | `llm_client.get_openai_client` (통합) |

> 내부 구현·싱글톤 패턴은 기존과 동일.

### 4.3 `embeddings.py` (유지)
- 변경 없음.

### 4.4 `slot_extractor.py` (신규 - 3개 파일 통합)
| 원본 | → 이동 후 |
|---|---|
| `embedding_service.py::_make_embedding_slot_json` | `slot_extractor._make_embedding_slot_json` |
| `embedding_service.py::EmbeddingSearchService.extract_slots` | `slot_extractor` 모듈 함수화 (호출 경로는 `@tool` 통해서) |
| `embedding_tool.py::embedding_slot_extract` (`@tool`) | `slot_extractor.embedding_slot_extract` |
| `llm_tool2.py::_make_fixed_search_json` | `slot_extractor._make_fixed_search_json` |
| `llm_tool2.py::_parse_fixed_search_json` | `slot_extractor._parse_slot_json` (공용화) |
| `llm_tool2.py::fixed_search` (`@tool`) | `slot_extractor.fixed_search` |

> 두 슬롯 추출기(`embedding` / `fixed`)는 JSON schema 와 프롬프트만 다르고 파싱·클라이언트·스키마 구조는 동일 → 한 파일로 합치는 것이 자연스러움.

### 4.5 `retriever.py` (신규)
| 원본 | → 이동 후 |
|---|---|
| `generate.py::simple_retrieve_restaurants` | `retriever.simple_retrieve_restaurants` |

### 4.6 `generator.py` (신규, `generate.py` 리네임)
| 원본 | → 이동 후 |
|---|---|
| `generate.py::_SESSION_MESSAGES` | `generator._SESSION_MESSAGES` |
| `generate.py::clear_session` | `generator.clear_session` |
| `generate.py::get_llm` | `generator.get_llm` |
| `generate.py::generate_response` | `generator.generate_response` (내부에서 `retriever`, `prompts` 를 import) |

### 4.7 `router.py` (신규)
| 원본 | → 이동 후 |
|---|---|
| `pipeline.py::decide_route` | `router.decide_route` (프롬프트만 `prompts.ROUTER_PROMPT` 참조로 교체) |

### 4.8 `pipeline.py` (수정)
- 유지: `GraphState`, `_normalize_connector_response`, `route_node`, `embedding_slot_node`, `fixed_slot_node`, `connector_prepare_node`, `generate_node`, `route_condition`, `build_graph`, `get_graph`, `run_qa`
- 추가: `main()` CLI 진입점 (기존 `src/main.py` 내용)
- 추가: `if __name__ == "__main__": main()`
- import 경로만 재연결.

### 4.9 `mock_data.py` (신규)
- CLI Q&A 테스트용 최소 `restaurant_list` 샘플 (system_prompt가 기대하는 스키마에 맞춘 2~3건).
- 운영/테스트 DB 커넥터가 붙기 전까지 임시 데이터 소스.

---

## 5. 모듈 의존 그래프 (리팩터 이후)

```
config  ─┬─► embeddings
         ├─► llm_client
         ├─► prompts
         ├─► generator
         └─► router

llm_client ─┬─► slot_extractor
prompts    ─┤
prompts    ─► router
retriever  ─► generator
prompts    ─► generator

slot_extractor ─┐
router         ─┤
generator      ─┼─► pipeline ─► (CLI main)
mock_data      ─┘
```

순환 없음.

---

## 6. CLI 실행 방법 (리팩터 완료 후)

프로젝트 루트에서:
```powershell
python -m src.pipeline
```

동작:
1. `질문 >` 프롬프트가 뜸
2. 질문 입력 → `mock_data.restaurant_list`를 connector 응답으로 주입
3. LangGraph 파이프라인 실행 (route → slot extract → connector prepare → generate)
4. `[답변]`이 출력됨
5. 빈 Enter로 종료

---

## 7. 변경 영향 범위

- `src/__init__.py` : 그대로 둠 (패키지 마커).
- 외부에서 `from src.pipeline import run_qa` 처럼 import 하는 코드는 그대로 유지됨.
- `from src.main import ...` 같이 사용하는 외부 코드는 없다고 확인됨 (레포 전수 검색 완료).
- 루트 `main.py`(Streamlit 프런트)는 `src.pipeline.run_qa`를 장차 사용할 수 있으나 이번 리팩터 범위에선 손대지 않음.
