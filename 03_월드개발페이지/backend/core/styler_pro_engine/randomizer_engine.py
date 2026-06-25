"""
Randomizer Engine v1.0 (양산형 회피 엔진)
매 생성 시 구조·문체·CTA·FAQ 등을 랜덤화하여 양산형 패턴을 회피한다.
"""

import random
import time


def _make_seed():
    """매 호출마다 고유 시드 생성 (시간 + 랜덤 결합)."""
    return int(time.time() * 1000) ^ random.randint(0, 0xFFFFFF)


# ── 문체 랜덤화 ───────────────────────────────────────────────

STYLE_POOL = [
    {"id": "friendly", "label": "해요체 (친근)", "weight": 40,
     "instruction": "친근하고 상냥한 대화체(해요체)로, 독자에게 바로 옆에서 이야기하듯 작성하십시오."},
    {"id": "professional", "label": "하십시오체 (격식)", "weight": 30,
     "instruction": "신뢰감 있고 논리 정연하며 품격 있는 문체(하십시오체)로 작성하십시오."},
    {"id": "mixed", "label": "혼합체", "weight": 20,
     "instruction": "인트로와 결론은 해요체, 본문 핵심 설명은 하십시오체로 자연스럽게 혼합하여 작성하십시오."},
    {"id": "storytelling", "label": "이야기체", "weight": 10,
     "instruction": "실제 경험담을 풀어놓듯 이야기체로 몰입감 있게 작성하십시오. 예시를 풍부하게 섞으십시오."},
]


def pick_style(forced_style=None):
    """문체를 가중 랜덤으로 선택. forced_style이 주어지면 해당 스타일 고정."""
    if forced_style:
        for s in STYLE_POOL:
            if s["id"] == forced_style:
                return s
    # 가중 랜덤
    population = STYLE_POOL
    weights = [s["weight"] for s in population]
    return random.choices(population, weights=weights, k=1)[0]


# ── CTA 스타일 랜덤화 ─────────────────────────────────────────

CTA_STYLE_POOL = [
    {"id": "card", "label": "카드형", "weight": 30},
    {"id": "banner", "label": "배너형", "weight": 25},
    {"id": "inline", "label": "인라인형", "weight": 20},
    {"id": "button", "label": "버튼형", "weight": 15},
    {"id": "sidebar", "label": "사이드바형", "weight": 10},
]

CTA_POSITION_POOL = [
    ["목차 아래", "본문 중간", "FAQ 위"],
    ["인트로 아래", "표 아래", "결론 위"],
    ["목차 아래", "H2-2 아래", "FAQ 아래"],
    ["인트로 아래", "본문 중간", "결론 아래"],
]


def pick_cta_config():
    """CTA 디자인과 배치 위치를 랜덤으로 선택."""
    weights = [c["weight"] for c in CTA_STYLE_POOL]
    style = random.choices(CTA_STYLE_POOL, weights=weights, k=1)[0]
    positions = random.choice(CTA_POSITION_POOL)
    return {"style": style, "positions": positions}


# ── FAQ 랜덤화 ─────────────────────────────────────────────────

def randomize_faq(faq_items, target_count=None):
    """FAQ 목록을 셔플하고 개수를 가변 조정."""
    if not faq_items:
        return []

    shuffled = list(faq_items)
    random.shuffle(shuffled)

    if target_count is None:
        # 5~15개 범위에서 랜덤
        target_count = random.randint(5, min(15, len(shuffled)))

    # 번호 재매김
    result = shuffled[:target_count]
    for i, item in enumerate(result):
        q = item.get("question", "")
        a = item.get("answer", "")
        # Q/A 번호 제거 후 재부여
        import re
        q_clean = re.sub(r'^Q\d+[\.\s]*', '', q).strip()
        a_clean = re.sub(r'^A\d+[\.\s]*', '', a).strip()
        result[i] = {
            "question": f"Q{i+1}. {q_clean}",
            "answer": f"A{i+1}. {a_clean}"
        }

    return result


# ── 표 구성 랜덤화 ────────────────────────────────────────────

TABLE_COLOR_SCHEMES = [
    {"header_bg": "#a7eecf", "row_bg": "#e0f8e8", "border": "#000"},
    {"header_bg": "#bfdbfe", "row_bg": "#eff6ff", "border": "#1e3a5f"},
    {"header_bg": "#fde68a", "row_bg": "#fefce8", "border": "#78350f"},
    {"header_bg": "#e9d5ff", "row_bg": "#faf5ff", "border": "#581c87"},
    {"header_bg": "#fecaca", "row_bg": "#fef2f2", "border": "#7f1d1d"},
    {"header_bg": "#d1d5db", "row_bg": "#f3f4f6", "border": "#374151"},
]


def pick_table_style():
    """표 배색 스킴을 랜덤 선택."""
    return random.choice(TABLE_COLOR_SCHEMES)


# ── 강조 박스 스타일 랜덤화 ────────────────────────────────────

HIGHLIGHT_BOX_POOL = [
    {"type": "tip", "icon": "💡", "label": "꿀팁",
     "bg": "#f0fdf4", "border_color": "#16a34a", "text_color": "#166534"},
    {"type": "warning", "icon": "⚠️", "label": "주의사항",
     "bg": "#fffbeb", "border_color": "#d97706", "text_color": "#b45309"},
    {"type": "info", "icon": "ℹ️", "label": "참고",
     "bg": "#eff6ff", "border_color": "#2563eb", "text_color": "#1e40af"},
    {"type": "check", "icon": "✅", "label": "체크포인트",
     "bg": "#ecfdf5", "border_color": "#059669", "text_color": "#065f46"},
    {"type": "star", "icon": "⭐", "label": "핵심 요약",
     "bg": "#fefce8", "border_color": "#ca8a04", "text_color": "#854d0e"},
]


def pick_highlight_boxes(count=2):
    """본문 내 삽입할 강조 박스 스타일을 랜덤 선택."""
    pool = list(HIGHLIGHT_BOX_POOL)
    random.shuffle(pool)
    return pool[:min(count, len(pool))]


# ── H2/H3 구조 순서 랜덤화 ────────────────────────────────────

def shuffle_section_order(sections, keep_first=True, keep_last=True):
    """H2 섹션 순서를 랜덤화. 첫 번째(개요)와 마지막(FAQ/결론)은 고정 옵션."""
    if len(sections) <= 2:
        return sections

    first = [sections[0]] if keep_first else []
    last = [sections[-1]] if keep_last else []

    start = 1 if keep_first else 0
    end = -1 if keep_last else len(sections)
    middle = list(sections[start:end] if end != len(sections) else sections[start:])

    random.shuffle(middle)
    return first + middle + last


# ── 제목 스타일 랜덤화 ────────────────────────────────────────

TITLE_STYLE_WEIGHTS = {
    "정보형": 15, "비교형": 12, "리스트형": 12, "후기형": 10, "충격형": 8,
    "실수방지형": 10, "전문가형": 8, "최신뉴스형": 10, "질문형": 8, "가이드형": 7,
}


def pick_title_style():
    """제목 유형을 가중 랜덤으로 선택."""
    types = list(TITLE_STYLE_WEIGHTS.keys())
    weights = list(TITLE_STYLE_WEIGHTS.values())
    return random.choices(types, weights=weights, k=1)[0]


# ── 통합 랜덤화 프로필 생성 ────────────────────────────────────

def generate_randomization_profile(forced_style=None):
    """
    한 번의 글 생성에 사용할 전체 랜덤화 프로필을 생성한다.
    이 프로필을 content_builder에 전달하면 양산형 회피가 적용된다.
    
    Returns:
        {
            "seed": int,
            "style": { ... },
            "cta": { ... },
            "title_type": str,
            "table_color": { ... },
            "highlight_boxes": [ ... ],
            "faq_shuffle": bool,
            "section_shuffle": bool
        }
    """
    seed = _make_seed()
    random.seed(seed)

    return {
        "seed": seed,
        "style": pick_style(forced_style),
        "cta": pick_cta_config(),
        "title_type": pick_title_style(),
        "table_color": pick_table_style(),
        "highlight_boxes": pick_highlight_boxes(count=random.randint(1, 3)),
        "faq_shuffle": True,
        "section_shuffle": random.random() > 0.3,  # 70% 확률로 섹션 순서 셔플
    }


if __name__ == "__main__":
    profile = generate_randomization_profile()
    print(json.dumps(profile, ensure_ascii=False, indent=2, default=str))
    import json
