"""CLI 질의응답 테스트용 Mock restaurant_list.

실제 DB 커넥터가 붙기 전까지 `pipeline.main()`에서 사용되는 임시 샘플.
`prompts/system_prompt.txt`가 기대하는 스키마에 맞춰 최소 필드만 채움.
"""
from __future__ import annotations


restaurant_list: list[dict] = [
    {
        "restaurant_code": "RES0001",
        "name": "강남 파스타 연구소",
        "img_link": "https://example.com/img1.jpg",
        "region": "서울",
        "address": "서울 강남구 강남대로 123",
        "tel_no": "000-0000-0000",
        "category": ["이탈리안", "파스타", "캐주얼다이닝"],
        "tags": ["데이트", "파스타맛집", "분위기좋음"],
        "lat": 37.4979,
        "lng": 127.0276,
        "open_time": "11:00",
        "close_time": "22:00",
        "menus": [
            {"name": "까르보나라", "price": 14000, "description": "크리미한 까르보나라"},
            {"name": "알리오 올리오", "price": 12000, "description": "마늘 오일 파스타"},
            {"name": "라자냐", "price": 15000, "description": "정통 라자냐"},
            {"name": "스테이크", "price": 28000, "description": "그릴 스테이크"},
            {"name": "시저 샐러드", "price": 9000, "description": "신선한 샐러드"}
        ],
        "reviews": [
            {
                "name": "먹잘알_민수",
                "avg_score": 3.5,
                "review_cnt": 20,
                "follower_cnt": 5,
                "score": 4.0,
                "taste_level": 3,
                "price_level": 2,
                "service_level": 3,
                "tags": ["맛있음", "분위기좋음"],
                "content": "파스타가 꽤 괜찮았어요.",
                "menu": "까르보나라"
            },
            {
                "name": "맛집탐험가",
                "avg_score": 4.0,
                "review_cnt": 50,
                "follower_cnt": 20,
                "score": 5.0,
                "taste_level": 4,
                "price_level": 3,
                "service_level": 4,
                "tags": ["추천"],
                "content": "재방문 의사 있습니다.",
                "menu": "라자냐"
            },
            {
                "name": "평범한직장인",
                "avg_score": 3.0,
                "review_cnt": 10,
                "follower_cnt": 2,
                "score": 3.0,
                "taste_level": 3,
                "price_level": 2,
                "service_level": 2,
                "tags": ["무난"],
                "content": "전체적으로 무난한 느낌.",
                "menu": "알리오 올리오"
            }
        ]
    },

    {
        "restaurant_code": "RES0002",
        "name": "이태원 스시바",
        "img_link": "https://example.com/img2.jpg",
        "region": "서울",
        "address": "서울 용산구 이태원로 45",
        "tel_no": "000-0000-0000",
        "category": ["일식", "스시"],
        "tags": ["스시맛집", "고급"],
        "lat": 37.5345,
        "lng": 126.9940,
        "open_time": "12:00",
        "close_time": "21:30",
        "menus": [
            {"name": "오마카세", "price": 50000, "description": "셰프 추천 코스"},
            {"name": "연어초밥", "price": 15000, "description": "신선한 연어"},
            {"name": "참치초밥", "price": 18000, "description": "고급 참치"},
            {"name": "튀김세트", "price": 12000, "description": "바삭한 튀김"},
            {"name": "우동", "price": 9000, "description": "따뜻한 국물"}
        ],
        "reviews": [
            {
                "name": "초밥러버",
                "avg_score": 4.2,
                "review_cnt": 80,
                "follower_cnt": 30,
                "score": 5.0,
                "taste_level": 5,
                "price_level": 4,
                "service_level": 4,
                "tags": ["신선함"],
                "content": "재료가 정말 신선해요.",
                "menu": "오마카세"
            },
            {
                "name": "직장인점심러",
                "avg_score": 3.8,
                "review_cnt": 40,
                "follower_cnt": 10,
                "score": 4.0,
                "taste_level": 4,
                "price_level": 3,
                "service_level": 3,
                "tags": ["괜찮음"],
                "content": "가격 대비 만족스럽습니다.",
                "menu": "연어초밥"
            },
            {
                "name": "가끔외식",
                "avg_score": 3.5,
                "review_cnt": 15,
                "follower_cnt": 5,
                "score": 3.0,
                "taste_level": 3,
                "price_level": 3,
                "service_level": 3,
                "tags": ["보통"],
                "content": "평범한 편이에요.",
                "menu": "우동"
            }
        ]
    },

    {
        "restaurant_code": "RES0003",
        "name": "홍대 고기집",
        "img_link": "https://example.com/img3.jpg",
        "region": "서울",
        "address": "서울 마포구 홍익로 78",
        "tel_no": "000-0000-0000",
        "category": ["한식", "고기"],
        "tags": ["삼겹살", "회식"],
        "lat": 37.5563,
        "lng": 126.9236,
        "open_time": "16:00",
        "close_time": "23:00",
        "menus": [
            {"name": "삼겹살", "price": 13000, "description": "국내산 돼지고기"},
            {"name": "갈비", "price": 25000, "description": "양념 갈비"},
            {"name": "김치찌개", "price": 8000, "description": "진한 국물"},
            {"name": "냉면", "price": 9000, "description": "시원한 면요리"},
            {"name": "소주", "price": 5000, "description": "기본 주류"}
        ],
        "reviews": [
            {
                "name": "고기장인",
                "avg_score": 4.0,
                "review_cnt": 60,
                "follower_cnt": 15,
                "score": 5.0,
                "taste_level": 5,
                "price_level": 3,
                "service_level": 4,
                "tags": ["고기맛집"],
                "content": "고기가 정말 맛있습니다.",
                "menu": "삼겹살"
            },
            {
                "name": "회식러",
                "avg_score": 3.7,
                "review_cnt": 25,
                "follower_cnt": 7,
                "score": 4.0,
                "taste_level": 4,
                "price_level": 3,
                "service_level": 3,
                "tags": ["회식추천"],
                "content": "단체로 가기 좋아요.",
                "menu": "갈비"
            },
            {
                "name": "소소한일상",
                "avg_score": 3.2,
                "review_cnt": 12,
                "follower_cnt": 3,
                "score": 3.0,
                "taste_level": 3,
                "price_level": 2,
                "service_level": 2,
                "tags": ["무난"],
                "content": "그냥 평범합니다.",
                "menu": "김치찌개"
            }
        ]
    },

    {
        "restaurant_code": "RES0004",
        "name": "마포 비건정원",
        "img_link": "https://example.com/img4.jpg",
        "region": "서울",
        "address": "서울 마포구 월드컵북로 22",
        "tel_no": "000-0000-0000",
        "category": ["비건", "건강식"],
        "tags": ["비건식", "다이어트"],
        "lat": 37.5637,
        "lng": 126.9084,
        "open_time": "10:00",
        "close_time": "20:00",
        "menus": [
            {"name": "비건 샐러드볼", "price": 11000, "description": "신선한 채소"},
            {"name": "두부 스테이크", "price": 13000, "description": "담백한 두부"},
            {"name": "과일 스무디", "price": 7000, "description": "상큼한 음료"},
            {"name": "아보카도 토스트", "price": 9000, "description": "건강식"},
            {"name": "야채 스프", "price": 8000, "description": "따뜻한 수프"}
        ],
        "reviews": [
            {
                "name": "헬시라이프",
                "avg_score": 4.1,
                "review_cnt": 30,
                "follower_cnt": 12,
                "score": 5.0,
                "taste_level": 4,
                "price_level": 3,
                "service_level": 4,
                "tags": ["건강식"],
                "content": "가볍고 좋네요.",
                "menu": "비건 샐러드볼"
            },
            {
                "name": "비건입문자",
                "avg_score": 3.9,
                "review_cnt": 18,
                "follower_cnt": 6,
                "score": 4.0,
                "taste_level": 4,
                "price_level": 3,
                "service_level": 3,
                "tags": ["추천"],
                "content": "입문용으로 좋습니다.",
                "menu": "두부 스테이크"
            },
            {
                "name": "가끔건강",
                "avg_score": 3.0,
                "review_cnt": 8,
                "follower_cnt": 2,
                "score": 3.0,
                "taste_level": 3,
                "price_level": 2,
                "service_level": 2,
                "tags": ["무난"],
                "content": "특별하진 않아요.",
                "menu": "야채 스프"
            }
        ]
    },

    {
        "restaurant_code": "RES0005",
        "name": "신촌 버거공장",
        "img_link": "https://example.com/img5.jpg",
        "region": "서울",
        "address": "서울 서대문구 신촌로 9",
        "tel_no": "000-0000-0000",
        "category": ["패스트푸드", "버거"],
        "tags": ["가성비", "간편식"],
        "lat": 37.5595,
        "lng": 126.9423,
        "open_time": "10:30",
        "close_time": "23:30",
        "menus": [
            {"name": "치즈버거", "price": 7000, "description": "기본 버거"},
            {"name": "더블버거", "price": 9000, "description": "패티 2장"},
            {"name": "감자튀김", "price": 3000, "description": "사이드 메뉴"},
            {"name": "콜라", "price": 2000, "description": "음료"},
            {"name": "치킨버거", "price": 8000, "description": "치킨 패티"}
        ],
        "reviews": [
            {
                "name": "버거덕후",
                "avg_score": 3.6,
                "review_cnt": 45,
                "follower_cnt": 10,
                "score": 4.0,
                "taste_level": 4,
                "price_level": 4,
                "service_level": 3,
                "tags": ["가성비"],
                "content": "가격 대비 괜찮아요.",
                "menu": "치즈버거"
            },
            {
                "name": "간단식사",
                "avg_score": 3.3,
                "review_cnt": 20,
                "follower_cnt": 5,
                "score": 3.0,
                "taste_level": 3,
                "price_level": 3,
                "service_level": 3,
                "tags": ["무난"],
                "content": "평범한 맛입니다.",
                "menu": "더블버거"
            },
            {
                "name": "야식러",
                "avg_score": 3.8,
                "review_cnt": 12,
                "follower_cnt": 4,
                "score": 4.0,
                "taste_level": 4,
                "price_level": 3,
                "service_level": 3,
                "tags": ["추천"],
                "content": "간단하게 먹기 좋아요.",
                "menu": "치킨버거"
            }
        ]
    }
]
