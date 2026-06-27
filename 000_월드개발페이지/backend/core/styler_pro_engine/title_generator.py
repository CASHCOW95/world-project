import os
import sys
import json
import argparse
HAS_GEMINI = False
try:
    from google.generativeai import GenerativeModel
    import google.generativeai as genai
    HAS_GEMINI = True
except Exception:
    HAS_GEMINI = False

# 10 Request title categories
CATEGORIES = [
    "정보형", "비교형", "리스트형", "후기형", "충격형",
    "실수방지형", "전문가형", "최신뉴스형", "질문형", "가이드형"
]

def generate_100_titles(keyword, category):
    api_key = os.environ.get("GEMINI_API_KEY", "")
    
    if HAS_GEMINI and api_key.strip():
        try:
            genai.configure(api_key=api_key)
            model = GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            당신은 15년차 수익형 블로그 SEO 전문가이자 클릭율을 극대화하는 카피라이터입니다.
            제시된 카테고리와 키워드를 기반으로, 독자의 호기심을 유발하고 구글/네이버 상위 노출에 최적화된 매혹적인 블로그 제목 100개를 생성하십시오.
            
            [대상 카테고리]: {category}
            [핵심 키워드]: {keyword}
            
            [생성 규칙]:
            1. 아래의 10개 제목 장르별로 정확히 10개씩의 제목을 생성하십시오:
               - 정보형: 핵심 개념, 조건, 정의를 명확히 알리는 제목
               - 비교형: 대상간 혜택이나 은행, 방법 등을 대조 비교하는 제목
               - 리스트형: 숫자와 목록을 엮어 체계적으로 보여주는 제목
               - 후기형: 실제 사용기나 내돈내산, 생생한 후기를 모티브로 한 제목
               - 충격형: 호기심과 긴장감을 자극하여 강력한 클릭을 유도하는 제목
               - 실수방지형: 신청 오류, 반려, 실패 원인 등을 짚어 경각심을 주는 제목
               - 전문가형: 권위자, 15년차 베테랑, 컨설턴트 관점을 적용한 제목
               - 최신뉴스형: 2026 최신 소식, 개정안, 속보, 실시간 일정 요약 제목
               - 질문형: 독자의 핵심 의문을 의문문으로 엮은 제목
               - 가이드형: 초보자 입문, A to Z, 완벽 정리, 바이블 템플릿 제목
            2. 총 100개의 제목이 도출되어야 하며, 키워드가 자연스럽게 제목 내에 녹아들게 하십시오.
            3. 반환 데이터는 반드시 아래의 JSON 형식으로만 응답하고, 백틱(```json)이나 다른 설명 글은 절대 포함하지 마십시오.
            
            {{
              "titles": [
                {{ "type": "정보형", "title": "생성된 제목 1" }},
                ...
              ]
            }}
            """
            response = model.generateContent(prompt)
            raw_text = response.text.strip()
            
            import re
            if raw_text.startswith("```"):
                raw_text = re.sub(r'^```json\s*', '', raw_text, flags=re.IGNORECASE)
                raw_text = re.sub(r'```$', '', raw_text).strip()
                
            parsed = json.loads(raw_text)
            if "titles" in parsed and len(parsed["titles"]) > 0:
                return parsed["titles"]
                
        except Exception as e:
            sys.stderr.write(f"Gemini title generation failed: {str(e)}. Using fallback.\n")
            
    # Mock Fallback Title Matrix (10 styles * 10 templates each)
    mock_titles = []
    
    templates = {
        "정보형": [
            "{keyword} 핵심 조건 및 대상자 기준 완벽 정리",
            "모르면 손해! {keyword} 꼭 확인해야 하는 핵심 3가지",
            "2026년식 {keyword} 자격 기준과 신청 지원 상세 분석",
            "{keyword}이란 무엇인가? 초보자용 개념 총론",
            "{keyword} 혜택 혜수기 및 금전적 효과 안내",
            "{keyword} 제출 서류 목록 및 발급 수수료 정보",
            "{keyword} 놓치기 쉬운 기본 조항과 예외 기준",
            "{keyword} 시행 목적과 주요 변경 내역 요약",
            "{keyword} 신규 대상자 추가 선정 소식 총정리",
            "{keyword} 신청 기한 및 월별 지급일 스케줄"
        ],
        "비교형": [
            "A사 vs B사 {keyword} 혜택 차이점 끝장 비교",
            "나에게 맞는 {keyword} 유형별 차이점 및 추천 가이드",
            "은행별 {keyword} 우대 조건 및 수수료 최저치 비교",
            "전국 {keyword} 지역별 혜택 및 추가금 규모 전격 비교",
            "{keyword} 온라인 신청 vs 오프라인 방문 장단점 비교",
            "단기 vs 장기 관점에서 본 {keyword} 기대효과 비교 분석",
            "20대부터 60대까지 연령대별 {keyword} 적용 기준 비교",
            "무료형 vs 유료형 {keyword} 실무적 성능 차이점 비교",
            "유사 지원책 vs {keyword} 어떤 것이 나에게 더 유리할까?",
            "신규 상품 vs 기존 상품 {keyword} 혜택 보강 비교"
        ],
        "리스트형": [
            "{keyword} 성공 확률 높이는 10가지 추천 체크리스트",
            "{keyword} 관련 가장 많이 찾는 대표 사이트 TOP 5",
            "{keyword} 진행 시 반드시 준비해야 할 7가지 서류",
            "{keyword} 만족도 최상! 유저가 꼽은 꿀팁 8가지",
            "시간을 아껴주는 {keyword} 빠른 처리 순서 TOP 4",
            "{keyword} 필수 확인해야 할 유관 기관 목록 6선",
            "전문가들이 권장하는 {keyword} 활성화 전술 5가지",
            "반려 없는 {keyword} 통과 비법 리스트 TOP 3",
            "{keyword} 관련 자주 묻는 질문 10선 모음",
            "{keyword} 시 정독해야 하는 관련 법령 가이드라인 TOP 7"
        ],
        "후기형": [
            "직접 신청해본 {keyword} 솔직한 내돈내산 찐후기",
            "반려 극복! {keyword} 우여곡절 끝에 승인받은 생생 후기",
            "지인에게 강력 추천받은 {keyword} 1개월차 사용 리뷰",
            "생각보다 간단했던 {keyword} 실제 대리 신청 성공 후기",
            "{keyword} 실패 사례를 통해 본 리얼 극복 스토리 후기",
            "주부 입장에서 작성한 {keyword} 생활비 절약 성공 리뷰",
            "1인 창업자가 말하는 {keyword} 지원금 지급 및 사용 후기",
            "부모님 모시고 다녀온 {keyword} 상세 체험 후기 분석",
            "아무 준비 없이 도전했던 {keyword} 리얼한 후폭풍 리뷰",
            "직장인 주말 찬스 활용 {keyword} 당일 완료 성공 후기"
        ],
        "충격형": [
            "아무도 가르쳐주지 않는 {keyword}의 숨겨진 비밀",
            "모르면 평생 100% 후회하는 {keyword}의 실체",
            "설마 했던 {keyword}, 내 계좌도 털릴 수 있다?",
            "정부가 숨겨온 {keyword}의 충격적인 진실",
            "대기업이 몰래 쓰는 {keyword} 핵심 비법 대공개",
            "이걸 모르면 {keyword} 신청해봤자 헛수고입니다",
            "소문만 무성했던 {keyword} 직접 파헤쳐본 소름 돋는 진실",
            "지인의 경고! {keyword} 함부로 진입했다가 겪는 참패",
            "하루아침에 300만원 아끼는 {keyword} 미친 전환율의 비밀",
            "더 이상 속지 마세요! {keyword} 광고와 다른 실제 혜택"
        ],
        "실수방지형": [
            "{keyword} 신청할 때 90%가 저지르는 치명적 실수 5가지",
            "이것만 피하면 승인 완료! {keyword} 탈락 원인 분석",
            "{keyword} 기한 놓치면 평생 소급 불가능! 주의사항",
            "{keyword} 계좌 등록 시 오류 해결법 및 재신청 가이드",
            "중도 해지 시 폭망? {keyword} 가입 전 필수 숙지사항",
            "{keyword} 대행 사기 예방하는 안전 계약 수칙 3가지",
            "제출 서류 누락 방지! {keyword} 자가 진단 가이드",
            "{keyword} 조건 미달로 거절당했을 때 대처 로직",
            "동의서 서명 실수로 기각된 {keyword} 살리는 방법",
            "연체 이력 있을 때 {keyword} 심사 통과하는 비법"
        ],
        "전문가형": [
            "15년차 블로그 SEO 전문가가 파헤친 {keyword} 성공 전략",
            "금융 컨설턴트가 제안하는 {keyword} 최적의 포트폴리오",
            "법률 전문가 자문 필독! {keyword} 권리분석 핵심 바이블",
            "의료인 조언 포함! {keyword} 부작용 없이 올바르게 처방받는 법",
            "세무사가 권하는 {keyword} 활용 절세 혜택 극대화 루트",
            "베테랑 셀러가 독점하는 {keyword} 상위 노출 절대 법칙",
            "은퇴 컨설턴트 분석: {keyword} 노후 연금과 결합하는 비결",
            "IT 수석 아키텍트가 검증한 {keyword} 자동화 연결 도구",
            "부동산 애널리스트가 진단한 {keyword} 입지별 가치 평가",
            "교육 전문가 특강! {keyword} 효율을 300% 높이는 공부 습관"
        ],
        "최신뉴스형": [
            "[속보] 2026년 {keyword} 법 개정 전면 공지 안내",
            "긴급 편성! {keyword} 추가 지원금 특별 추가 접수 개시",
            "오늘 자 발표 {keyword} 지역 요건 전격 해제 소식",
            "2026년 6월 최신 {keyword} 변경점 및 소득 제한 요약",
            "[단독] {keyword} 플랫폼 먹통 현상 및 우회 접수처 안내",
            "{keyword} 2차 모집 시작! 이번 기수 놓치면 1년 대기",
            "최근 트렌드 분석: {keyword} 시장 확대와 관련주 급등 현황",
            "실시간 이슈 정리: {keyword} 소비자 불만과 가이드라인 제정",
            "[오늘의 뉴스] {keyword} 간편 모바일 앱 전용 신청 오픈",
            "기습 완화! {keyword} 신용 점수 기준 하향 전격 단행"
        ],
        "질문형": [
            "프리랜서인 나도 {keyword} 대상자에 포함될 수 있을까?",
            "{keyword} 신청하면 도대체 언제쯤 내 통장에 입금되나요?",
            "신용등급 낮아도 {keyword} 무리 없이 승인받는 법은?",
            "{keyword} 다른 정책 자금과 중복 수령이 가능한가요?",
            "서류 제출 중 오타가 났는데 {keyword} 기각될까요?",
            "{keyword} 중간에 이사가면 지원금 끊기는 것 아닌가요?",
            "실제 후기 보니까 {keyword} 생각보다 별로라는데 진짜일까?",
            "{keyword} 어디서부터 어떻게 시작해야 할지 막막하다면?",
            "직장인 연말정산 시 {keyword} 소득공제 비율은 몇 퍼센트?",
            "부모님 대신 {keyword} 온라인 신청해드릴 때 대리인 자격은?"
        ],
        "가이드형": [
            "{keyword} 초보자를 위한 A to Z 완벽 마스터 바이블",
            "한 눈에 끝내는 {keyword} 종합 백서 및 핵심 지침서",
            "클릭 3번으로 끝! {keyword} 모바일 간편 신청 가이드",
            "{keyword} 수익화를 준비하는 분들을 위한 실전 전략서",
            "{keyword} 준비부터 최종 집행까지 단계별 무작정 따라하기",
            "바쁜 현대인을 위한 {keyword} 핵심만 요약한 3분 요약본",
            "{keyword} 성공적인 안착을 돕는 가이드북 PDF 무료 배포",
            "놓치면 나만 손해인 {keyword} 상세 백과사전 가이드",
            "{keyword} 실패 없는 원스톱 처리 공식 표준 매뉴얼",
            "{keyword} 생존율을 200% 올리는 실전 가이드라인"
        ]
    }
    
    # Render exactly 10 titles for each of the 10 types
    for t_type in CATEGORIES:
        title_list = templates.get(t_type, [])
        for t_idx, temp in enumerate(title_list):
            mock_titles.append({
                "type": t_type,
                "title": temp.format(keyword=keyword)
            })
            
    return mock_titles

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Styler Pro X V3 Title Generator")
    parser.add_argument("--keyword", type=str, required=True)
    parser.add_argument("--category", type=str, default="정부지원금")
    
    args = parser.parse_args()
    
    try:
        output = generate_100_titles(args.keyword, args.category)
        print("---JSON_START---")
        print(json.dumps(output, ensure_ascii=False))
        print("---JSON_END---")
    except Exception as e:
        import traceback
        sys.stderr.write(f"Title generator crashed: {str(e)}\n")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
