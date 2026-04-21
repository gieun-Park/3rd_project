"""프로젝트 전역에서 사용하는 프롬프트 상수 모음.

- EMBEDDING_SLOT_PROMPT: 임베딩 라우트에서 슬롯 추출용 프롬프트
- FIXED_SEARCH_PROMPT: 고정 검색(엔티티 직접 지정) 라우트의 슬롯 추출 프롬프트
- ROUTER_PROMPT: embedding / fixed 라우팅 판정 프롬프트
- load_system_prompt(): prompts/system_prompt.txt 를 읽어오는 헬퍼
"""
from __future__ import annotations

from .config import SETTINGS


EMBEDDING_SLOT_PROMPT = """너는 사용자의 검색 문장에서
식당 이름, 메뉴 이름, 유저 이름만 정확하게 추출하는 정보 추출기다.

반드시 JSON 객체만 반환해.
출력 형식은 정확히 {"restaurant": "...", "menu": "...", "user": "..."} 이어야 한다.

슬롯 정의:
- restaurant: 실제 존재하는 식당 이름 (고유명사)
- menu: 실제 음식/메뉴 이름 (예: 곱창전골, 파스타, 초밥 등)
- user: 리뷰어, 작성자, 닉네임 등 사람 이름

중요 규칙 (매우 중요):

1) restaurant에는 반드시 "실제 식당 이름"만 넣는다.
   - "맛집", "근처", "카페", "식당", "데이트", "분위기 좋은 곳" 같은 일반 표현은 절대 넣지 않는다.
   - 식당 이름이 명확히 없으면 빈 문자열("")로 둔다.

2) menu에는 음식/메뉴 이름만 넣는다.
   - 예: 곱창전골, 파스타, 초밥, 라면 등

3) user에는 사람 이름/닉네임만 넣는다.

4) 지역명(신대방삼거리, 강남 등), 조건(데이트, 조용한 등), 일반 검색어는
   restaurant에 넣지 말고 무시한다.

5) 추측하지 말 것.
   명확한 식당 이름이 없으면 restaurant는 반드시 "".

6) 반드시 3개의 키를 모두 포함하고, 없는 값은 ""로 둔다.

7) 설명 없이 JSON만 출력한다.

예시:

입력: 신대방삼거리 근처 곱창전골 맛집
출력: {"restaurant": "", "menu": "곱창전골", "user": ""}

입력: 강남 파스타 연구소 까르보나라
출력: {"restaurant": "강남 파스타 연구소", "menu": "까르보나라", "user": ""}

입력: 먹잘알_민수 추천 초밥집
출력: {"restaurant": "", "menu": "초밥", "user": "먹잘알_민수"}

입력: 분위기 좋은 데이트 카페
출력: {"restaurant": "", "menu": "", "user": ""}"""


FIXED_SEARCH_PROMPT = """너는 사용자의 식당 검색 문장에서 restaurant, menu, user 슬롯을 추출하는 정보 추출기다.
반드시 JSON 객체만 반환해.
출력 형식은 정확히 {"restaurant": "...", "menu": "...", "user": "..."} 이어야 한다.

슬롯 정의:
- restaurant: 실제 식당/카페/브랜드/매장 이름으로 직접 지칭된 표현
- menu: 사용자가 직접 언급한 음식명, 메뉴명, 요리명, 음료명
- user: 리뷰어, 작성자, 유저, 닉네임, 블로거, 인플루언서 등 사람 이름

중요 규칙:
1) restaurant에는 실제 상호명으로 직접 지칭된 표현만 넣는다.
2) 지역명, 장소명, "근처", "맛집", "카페", "식당", "음식점", "분위기 좋은", "데이트", "조용한" 같은 일반 탐색 표현은 restaurant에 넣지 않는다.
3) menu에는 사용자가 직접 말한 음식/메뉴만 넣는다.
4) user에는 사람 이름/닉네임만 넣는다.
5) 어떤 표현이 음식명일 수도 있고 상호명일 수도 있어 애매하면 추측하지 말고 해당 슬롯은 빈 문자열로 둔다.
6) 식당명, 메뉴명, 유저명이 동시에 등장하면 각각 해당 슬롯에 채운다.
7) 반드시 restaurant, menu, user 세 키를 모두 포함하고, 없으면 ""로 둔다.
8) 설명, 마크다운, 코드블록 없이 JSON만 출력한다.

예시:
입력: 신대방삼거리 근처 곱창전골 맛집
출력: {"restaurant": "", "menu": "곱창전골", "user": ""}

입력: 강남 파스타 연구소 까르보나라
출력: {"restaurant": "강남 파스타 연구소", "menu": "까르보나라", "user": ""}

입력: 먹잘알_민수 추천 초밥
출력: {"restaurant": "", "menu": "초밥", "user": "먹잘알_민수"}

입력: 분위기 좋은 데이트 카페
출력: {"restaurant": "", "menu": "", "user": ""}

입력: 곱창
출력: {"restaurant": "", "menu": "곱창", "user": ""}"""


ROUTER_PROMPT = """
너는 식당 검색 라우터다.
사용자 질문을 보고 반드시 아래 둘 중 하나만 반환해.

- embedding
- fixed

판단 기준:
1) 분위기, 상황, 취향, 특징, 평가, 조합 조건 중심이면 embedding
2) 특정 식당명, 특정 메뉴명, 특정 유저/리뷰어, 명시적 엔티티 검색이면 fixed
3) 지역명이 들어가더라도 핵심이 조건 기반 탐색이면 embedding
4) 애매하면 embedding

반드시 embedding 또는 fixed 중 하나의 단어만 출력해.

사용자 질문:
{question}
""".strip()


def load_system_prompt() -> str:
    if not SETTINGS.prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {SETTINGS.prompt_path}")
    return SETTINGS.prompt_path.read_text(encoding="utf-8")
