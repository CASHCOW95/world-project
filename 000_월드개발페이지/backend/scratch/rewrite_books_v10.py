import os
import re
import base64
import markdown
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BACKEND_ROOT = Path(__file__).resolve().parents[1]
RESEARCH_COIN_DIR = BACKEND_ROOT / 'research' / 'coin'
book_dir = str(RESEARCH_COIN_DIR / 'digitalnomad' / '책')

categories = [
    ("01_블로그_및_애드센스_자동화_교본.md", "01_블로그_및_애드센스_자동화_벤치마킹_가이드북.md", 1),
    ("02_AI_에이전트_및_프롬프트_교본.md", "02_AI_에이전트_및_프롬프트_벤치마킹_가이드북.md", 2),
    ("03_유튜브_및_영상_음악_자동화_교본.md", "03_유튜브_및_영상_음악_자동화_벤치마킹_가이드북.md", 3),
    ("04_AI_이미지_생성_교본.md", "04_AI_이미지_생성_벤치마킹_가이드북.md", 4),
    ("05_수익인증_및_비즈니스_트렌드_교본.md", "05_수익인증_및_비즈니스_트렌드_벤치마킹_가이드북.md", 5)
]

cat_folders = {
    1: "01_블로그_및_애드센스_자동화",
    2: "02_AI_에이전트_및_프롬프트",
    3: "03_유튜브_및_영상_음악_자동화",
    4: "04_AI_이미지_생성",
    5: "05_수익인증_및_비즈니스_트렌드"
}

TOOLS_INFO = {
    "고수익 황금 키워드": ["황금 키워드", "황금키워드", "키워드 발굴", "키워드 어시스턴트"],
    "고수익 멘토": ["고수익 멘토", "고수익멘토", "멘토 프로그램"],
    "꿀제목 생성기": ["꿀제목", "제목 생성기", "제목생성기"],
    "스타일러 프로": ["스타일러", "styler"],
    "감마AI": ["감마", "gamma"],
    "미드저니": ["미드저니", "midjourney"],
    "스레드 만능 생성기": ["스레드", "thread", "스레드 생성기"],
    "디노 지식인 봇": ["지식인", "지식in", "지식인 봇"],
    "Claude AI (MCP)": ["클로드", "claude", "mcp"],
    "Suno AI": ["suno", "수노"],
    "GPT-4o / ChatGPT": ["chatgpt", "gpt-4", "gpt-4o", "챗gpt"],
    "블로그스팟": ["블로그스팟", "blogspot", "블로그 스팟"],
    "워드프레스": ["워드프레스", "wordpress"],
    "티스토리": ["티스토리", "tistory"],
    "쿠팡 파트너스": ["쿠파스", "쿠팡 파트너스", "쿠팡파트너스"],
    "네이버 쇼핑커넥트": ["쇼핑커넥트", "쇼핑 커넥트"],
    "유튜브 API": ["유튜브 api", "youtube api"],
    "yt-dlp": ["yt-dlp", "ytdlp"],
    "캡컷": ["캡컷", "capcut"],
    "Vrew": ["vrew", "브루"],
    "ElevenLabs": ["일레븐랩스", "elevenlabs", "음성 생성"],
    "텔레그램 봇 API": ["텔레그램", "telegram"],
    "구글 서치 콘솔": ["서치 콘솔", "서치콘솔", "search console"],
    "네이버 서치 어드바이저": ["서치 어드바이저", "서치어드바이저", "search advisor"],
    "빙 웹마스터 도구": ["빙 웹마스터", "webmaster tool"],
    "다음 웹마스터 도구": ["다음 웹마스터", "daum 웹마스터"],
    "구글 애드센스": ["애드센스", "adsense"],
    "디노 5.5": ["디노 5.5", "디노5.5", "디노 5.0", "디노5.0"]
}

# Subsections by topic
subsections_by_topic = {
    "sns": {
        "main_sec_name": "스레드 콘텐츠 기획 및 작성",
        "sub_sec_name": "소셜 미디어 외부 유입 장치 연결",
        "text_title": "홍보용 문구 및 요약글 구성",
        "img_title": "시각 자료 및 단축 주소 준비",
        "traffic_title": "자동 업로드 및 링크 연결 실행"
    },
    "saju": {
        "main_sec_name": "사주 분석 글 및 콘텐츠 완성",
        "sub_sec_name": "블로그 관리 및 방문자 유입 연동",
        "text_title": "개인 맞춤형 운세 내용 작성",
        "img_title": "어울리는 삽화 및 카드 이미지 배치",
        "traffic_title": "자동 업로드 및 추천 통로 확보"
    },
    "affiliate": {
        "main_sec_name": "상품 비교 원고 및 상세 리뷰 완성",
        "sub_sec_name": "수익 링크 및 방문 유도 연동",
        "text_title": "인기 제품 정보 및 설명 글 작성",
        "img_title": "실제 상품 느낌의 고품질 그림 배치",
        "traffic_title": "수익 링크 단축 및 방문자 통로 연결"
    },
    "music": {
        "main_sec_name": "음원 제작 및 영상 기획",
        "sub_sec_name": "유튜브 등록 및 채널 활성화",
        "text_title": "노래 가사 및 대본 기획",
        "img_title": "인공지능 노래 작곡 및 배경 화면 제작",
        "traffic_title": "채널 등록 및 외부 방문자 유치"
    },
    "youtube": {
        "main_sec_name": "영상 기획 및 대본 작성",
        "sub_sec_name": "자막 배치 및 자동 편집 완성",
        "text_title": "정보성 원고 및 설명 자막 작성",
        "img_title": "설명용 사진 생성 및 영상 클립 연동",
        "traffic_title": "자막 배치 및 자동 편집 완성"
    },
    "agent": {
        "main_sec_name": "작동 환경 구축 및 연동",
        "sub_sec_name": "자동화 프로그램 구동",
        "text_title": "프로그램 설정 파일 및 코드 설정",
        "img_title": "컴퓨터 제어 가상 환경 구성",
        "traffic_title": "자동화 동작 모니터링 및 결과 확인"
    },
    "blog_setup": {
        "main_sec_name": "블로그 디자인 및 원고 발행 계획",
        "sub_sec_name": "검색창 노출 및 외부 방문자 유치",
        "text_title": "기본 화면 구성 및 테마 최적화",
        "img_title": "예약 글 목록 생성 및 자동 발행 준비",
        "traffic_title": "웹마스터 도구 연동 및 방문자 링크 배치"
    },
    "styler": {
        "main_sec_name": "블로그 대량 발행 본문 기획",
        "sub_sec_name": "수익형 통로 구축 및 유입 다각화",
        "text_title": "대량 글 쓰기용 주제 목록 및 제목 발굴",
        "img_title": "본문 완성 및 가독성 개선 작업",
        "traffic_title": "외부 소셜 미디어 및 외부 링크 연결"
    },
    "default": {
        "main_sec_name": "블로그 본문 기획 및 디자인",
        "sub_sec_name": "방문 통로 확보 및 외부 노출",
        "text_title": "방문자 요구에 맞는 본문 글 쓰기",
        "img_title": "시각적 이해를 돕는 설명 삽화 배치",
        "traffic_title": "검색 포털 등록 및 방문 유도 버튼 연결"
    }
}

# Jargon replacement mapping
replacements = {
    "포스팅": "블로그 글 쓰기",
    "백링크": "추천 링크 연결",
    "트래픽": "방문자 유입",
    "아웃라인": "글의 목차 구조",
    "H2/H3": "대주제와 소주제",
    "데이터 흐름": "작업 이동 경로",
    "시스템 구성도": "자동화 구성",
    "API": "연동 도구",
    "파이프라인": "자동화 순서",
    "파싱": "내용 추출",
    "마크다운": "기본 글 문서",
    "데이터베이스": "저장소",
    "빌드": "만들기",
    "플랫폼": "서비스 채널",
    "알고리즘": "노출 규칙",
    "프로그램": "자동화 도구",
    "코딩": "프로그램 작성",
    "코드": "프로그램 명령",
    "스크립트": "자동 명령 코드",
    "테마": "스킨",
    "서버": "컴퓨터 시스템",
    "웹 서버": "인터넷 주소 연결 컴퓨터",
    "로컬 호스트": "내 컴퓨터 가상 서버",
    "로컬호스트": "내 컴퓨터 가상 서버",
    "포트": "접속 통로",
    "제이슨": "설정 파일 정보",
    "json": "설정 파일 정보"
}

def clean_jargon(text):
    for eng, kor in replacements.items():
        text = re.sub(re.escape(eng), kor, text, flags=re.IGNORECASE)
    return text

def make_html_tool(name):
    return f'<span style="background-color: #eff6ff; color: #1d4ed8; padding: 4px 8px; border-radius: 6px; font-weight: bold; border: 1px solid #bfdbfe; font-size: 0.85em; display: inline-block; margin: 2px;">[T] {name}</span>'

def get_topic_info(title, transcript):
    title_lower = title.lower()
    text_lower = transcript.lower()
    
    if "스레드" in title_lower or "thread" in title_lower or "인스타" in title_lower or "sns" in title_lower:
        topic = "sns"
        short_action = "스레드 외부유입"
    elif "사주" in title_lower or "운세" in title_lower or "칠순" in title_lower or "사주" in text_lower:
        topic = "saju"
        short_action = "사주 자동 포스팅"
    elif any(kw in title_lower for kw in ["쿠파스", "쿠팡", "쇼핑커넥트", "제휴마케팅", "제휴 마케팅", "리뷰", "상품"]):
        topic = "affiliate"
        short_action = "제휴 마케팅 리뷰"
    elif any(kw in title_lower for kw in ["플레이리스트", "힐링 음악", "음악", "카페", "보컬", "노래", "suno", "수노"]):
        topic = "music"
        short_action = "음악 영상 자동화"
    elif any(kw in title_lower for kw in ["유튜브", "영상", "캡컷", "vrew", "브루", "대본", "쇼츠", "롱폼"]):
        topic = "youtube"
        short_action = "유튜브 영상 제작"
    elif any(kw in title_lower for kw in ["클로드", "claude", "mcp", "에이전트", "프로그램", "파이썬", "코드", "개발"]):
        topic = "agent"
        short_action = "AI 에이전트 개발"
    elif any(kw in title_lower for kw in ["블로그스팟", "blogspot", "워드프레스", "wordpress", "티스토리", "tistory", "애드센스", "승인", "세팅", "스킨"]):
        topic = "blog_setup"
        short_action = "블로그 사이트 세팅"
    elif any(kw in title_lower for kw in ["스타일러 프로", "styler pro", "출시", "한정수량", "파스텔", "1위"]):
        topic = "styler"
        short_action = "스타일러 프로 활용"
    else:
        topic = "default"
        short_action = "자동화 블로그 작업"
        
    info = subsections_by_topic[topic]
    return topic, short_action, info["main_sec_name"], info["sub_sec_name"], info["text_title"], info["img_title"], info["traffic_title"]

def get_default_tool_desc(tool_name, topic):
    descs = {
        "고수익 황금 키워드": {
            "affiliate": "쇼핑 검색어 중 광고 클릭당 수익 가치가 높아 실제 판매 수익으로 연결되는 핵심 검색어를 찾아냅니다.",
            "default": "검색창에 사람들이 자주 입력하면서도 광고 단가가 높은 알짜배기 검색어를 발굴합니다."
        },
        "고수익 멘토": {
            "affiliate": "메인 리뷰 글과 세부 제품 소개 글 사이에 내부 추천 링크를 엮어 방문자가 구매 링크까지 자연스럽게 이동하게 설계합니다.",
            "default": "큰 주제의 메인 글과 세부 설명 글을 유기적으로 엮어 방문자가 블로그 내에서 계속 머무르게 구조화합니다."
        },
        "꿀제목 생성기": {
            "default": "사람들이 검색창에서 글을 보았을 때 강한 호기심을 느끼고 클릭해 들어오도록 유도하는 후킹용 제목을 만듭니다."
        },
        "스타일러 프로": {
            "affiliate": "여러 쇼핑몰의 상품 리뷰 글 양식에 맞춰 설득력 있는 홍보 글을 자동으로 완성합니다.",
            "blog_setup": "사이트 승인을 빠르게 통과할 수 있도록 글머리와 목차가 정돈된 고퀄리티 본문을 생성합니다.",
            "default": "다양한 주제와 키워드를 기반으로 긴 분량의 가독성 좋은 블로그 글을 대량으로 작성합니다."
        },
        "감마AI": {
            "blog_setup": "복잡한 설명 대신 시각적으로 정보를 정리해 보여주는 카드형 정보 박스를 레이아웃에 맞춰 배치합니다.",
            "default": "목차를 바탕으로 본문 글의 핵심을 한눈에 요약해 보여주는 카드 형태의 설명 이미지를 빠르게 만듭니다."
        },
        "미드저니": {
            "music": "카페 음악의 편안한 감성에 어울리는 따뜻한 분위기의 움직이는 배경용 그림을 생성합니다.",
            "saju": "동양적인 운세 분위기나 신비로운 느낌의 별자리, 사주 일러스트를 고품질로 그려냅니다.",
            "youtube": "영상의 각 장면에서 설명하는 상황을 시각적으로 묘사하는 고화질 일러스트나 컷 이미지를 생성합니다.",
            "affiliate": "리뷰하려는 제품군과 어울리는 깔끔하고 매력적인 배경 소품 이미지를 제작합니다.",
            "default": "본문 글의 문맥과 흐름에 맞추어 독창적이고 눈길을 끄는 고품질 이미지를 생성합니다."
        },
        "스레드 만능 생성기": {
            "default": "블로그 주소를 단축 주소로 가공한 후 소셜 네트워크(스레드 등)에 자동으로 홍보 글을 배포합니다."
        },
        "디노 지식인 봇": {
            "default": "네이버 지식인에 올라온 질문에 자동으로 유용한 답변을 작성하고 내 블로그 링크로 연결해 외부 방문자를 끌어모읍니다."
        },
        "Claude AI (MCP)": {
            "agent": "컴퓨터 파일이나 프로그램을 제어하는 연동 규칙을 지정하여 내 비서처럼 자동화를 수행하게 만듭니다.",
            "default": "프로그램 소스 코드를 생성하고 컴퓨터 설정 파일과 도구를 원활하게 다룰 수 있도록 돕습니다."
        },
        "Suno AI": {
            "default": "영상의 분위기와 컨셉에 맞추어 보컬 목소리와 악기 연주가 포함된 완성도 높은 음원을 배경음악으로 생성합니다."
        },
        "GPT-4o / ChatGPT": {
            "agent": "복잡한 소스 코드의 오류를 수정하거나 자동화 명령을 내릴 수 있는 프롬프트 지침을 제공합니다.",
            "default": "주어진 주제와 단어에 맞춰 자연스러운 대화체나 전문적인 리뷰 설명글 원고를 빠르게 생성합니다."
        },
        "블로그스팟": {
            "default": "구글에서 서비스하는 블로그에 접속하여 글이 네이버나 구글 검색창에 노출되도록 기본 설정을 완료합니다."
        },
        "워드프레스": {
            "default": "나만의 개인 블로그 사이트를 세팅하고 자동 글 쓰기 연동을 위한 접속 정보(키값)를 등록합니다."
        },
        "티스토리": {
            "default": "카카오 블로그 사이트 내에 가독성 높은 내부 링크 버튼을 세팅하고 검색 포털 노출 설정을 최적화합니다."
        },
        "쿠팡 파트너스": {
            "default": "제품 정보와 연동되는 수익 링크 코드를 발급받아 블로그 글에 배치합니다."
        },
        "네이버 쇼핑커넥트": {
            "default": "네이버 쇼핑에서 판매량이 많고 수수료율이 높은 제휴 마케팅 제품들의 상품 정보와 가격 데이터를 가져옵니다."
        },
        "유튜브 API": {
            "default": "완성된 영상 파일과 설명 텍스트, 자막 정보 등을 내 유튜브 채널에 번거로운 과정 없이 일괄 자동 업로드합니다."
        },
        "yt-dlp": {
            "default": "분석하고자 하는 벤치마킹 유튜브 영상의 원본 오디오 파일과 번역용 자막 텍스트 데이터를 빠르게 내려받습니다."
        },
        "캡컷": {
            "default": "배경 영상과 자막, 그리고 목소리 음성을 합쳐서 스마트폰이나 컴퓨터로 손쉽게 쇼츠 영상을 편집합니다."
        },
        "Vrew": {
            "default": "영상의 음성을 인공지능이 분석하여 말소리와 화면에 딱 들어맞는 자막 타이밍을 자동으로 생성하고 편집합니다."
        },
        "ElevenLabs": {
            "default": "감정이 살아있고 숨소리까지 자연스러운 고품질의 목소리 음성 파일을 캐릭터별로 생성합니다."
        },
        "텔레그램 봇 API": {
            "default": "블로그 글 쓰기나 외부 유입 작업이 완료되었을 때 스마트폰 메신저(텔레그램)로 처리 결과를 실시간으로 전송받습니다."
        },
        "구글 서치 콘솔": {
            "default": "블로그 주소를 등록하여 내 글이 구글 검색창에 자동으로 수집되고 검색 결과에 노출되도록 설정합니다."
        },
        "네이버 서치 어드바이저": {
            "default": "내 사이트를 네이버에 등록하고 수집 상태를 진단하여 네이버 영역 노출을 활성화합니다."
        },
        "빙 웹마스터 도구": {
            "default": "빙 검색 포털에 사이트맵을 제출하여 해외 방문자들이 검색을 통해 내 글에 접속하게 만듭니다."
        },
        "다음 웹마스터 도구": {
            "default": "다음 포털 사이트에 내 블로그 정보와 RSS를 등록하여 다음 노출 환경을 활성화합니다."
        },
        "구글 애드센스": {
            "default": "내 블로그에 광고를 송출하여 방문자들이 광고를 볼 때 수익이 발생하도록 승인을 신청하고 연동합니다."
        },
        "디노 5.5": {
            "default": "자동 동영상 편집 기능을 지원하여 자막과 이미지를 매칭하고 빠른 시간 내에 영상을 제작해 줍니다."
        }
    }
    tool_desc = descs.get(tool_name, {})
    return tool_desc.get(topic, tool_desc.get("default", "관련 작업을 자동으로 진행하고 관리합니다."))

def get_tool_bullet(tool_name, topic, category_sentences):
    keywords = TOOLS_INFO.get(tool_name, [tool_name])
    for s in category_sentences:
        if any(kw.lower() in s.lower() for kw in keywords):
            cleaned = clean_jargon(s)
            # Make sure it ends nicely
            if not cleaned.endswith(('.', '!', '?')):
                cleaned += '.'
            return f"* **<span style='color: #2563eb; font-weight: bold;'>[T] {tool_name}</span>** : {cleaned}"
            
    desc = get_default_tool_desc(tool_name, topic)
    return f"* **<span style='color: #2563eb; font-weight: bold;'>[T] {tool_name}</span>** : {desc}"

def get_topic_tip(topic, title):
    tips = {
        "blog_setup": "블로그를 개설하고 초기에 방문자 유입이 저조하더라도 디자인을 수정하는 데 시간을 낭비하지 마십시오. 기본 스킨에 충실하고 글을 1개라도 더 작성하여 포털 노출량을 늘리는 것이 승인과 수익화의 지름길입니다.",
        "agent": "가상 비서의 명령 규칙을 작성할 때 오류가 발생한다면 설정 파일(JSON)의 괄호 닫힘과 따옴표 위치를 점검하십시오. 또한 바뀐 규칙이 올바르게 적용되도록 연동 도구를 재설행하여 다시 작동시킵니다.",
        "music": "음악 플레이리스트 영상을 올릴 때는 시청자가 첫 화면에서 이탈하지 않도록 시각적으로 매력적인 썸네일과 가사 자막 배치를 신경 쓰십시오. 저작권에 문제가 없는 장르와 목소리를 선정하는 것도 장기 채널 운영에 필수적입니다.",
        "youtube": "쇼츠 영상을 기획할 때는 첫 3초 이내에 시청자의 시선을 붙잡을 수 있는 강력한 문구나 움직임 효과를 주어야 알고리즘의 혜택을 받기 쉽습니다. 대본의 무음 구간은 자동 편집 도구로 완전히 제거해 속도감을 높이십시오.",
        "saju": "운세 분석이나 동양 사주 콘텐츠는 타겟층의 연령과 성별에 맞춘 감성적인 멘트와 시각 자료를 조화롭게 구성해야 공유율이 오릅니다. 글머리 타이틀에 핵심 내용을 한 문장으로 부각하십시오.",
        "sns": "소셜 네트워크 홍보 글은 글자 수 제한이 있으므로, 핵심 요약과 매력적인 후킹 문장을 맨 처음에 배치하십시오. 주소는 반드시 신뢰할 수 있는 단축 주소로 가공해야 유입 차단이 발생하지 않습니다.",
        "affiliate": "쇼핑 리뷰 글을 쓸 때는 단순한 스펙 나열 대신 소비자가 궁금해할 단점과 극복 방안을 함께 적어 신뢰도를 높이십시오. 짧은 주소로 변환한 추천 링크를 본문 하단 버튼에 깔끔하게 연결하는 것이 구매 유도에 좋습니다.",
        "styler": "대량의 글을 자동으로 생성할 때는 각 글의 문맥이 어색하지 않은지 초기 한두 번은 꼼꼼히 확인해 주는 것이 좋습니다. 발행 예약을 2~3시간 단위로 여유 있게 두어 기기의 부하를 줄이십시오.",
        "default": "자동화 시스템을 실행할 때는 처음부터 너무 완벽한 결과물을 기대하기보다 작동 단계를 하나씩 점검하며 점진적으로 기능을 확장해 나가는 것이 안정적입니다."
    }
    return tips.get(topic, tips["default"])

def rewrite_book_from_benchmark(md_filename, benchmark_filename, chapter_num):
    md_path = os.path.join(book_dir, md_filename)
    benchmark_path = os.path.join(book_dir, benchmark_filename)
    
    print(f"\n==================================================")
    print(f"Reading benchmark metadata from {benchmark_filename}...")
    with open(benchmark_path, 'r', encoding='utf-8') as f:
        benchmark_content = f.read()
        
    pattern = r'\d+\.\s+\*\*\[([\d\-]+)\]\*\*\s+(.*?)\s+\(🔗\s+\[영상\s+보기\]\((.*?)\)\)'
    video_list = re.findall(pattern, benchmark_content)
    
    if not video_list:
        print(f"Failed to find video list in benchmark file {benchmark_filename}")
        return
        
    print(f"Parsed {len(video_list)} videos for Chapter {chapter_num}")
    
    lectures_blocks = benchmark_content.split('### 📍 ')
    details_map = {}
    for block in lectures_blocks[1:]:
        lines = block.split('\n')
        title_line = lines[0].strip()
        clean_title = re.sub(r'^\d+단계:\s*', '', title_line)
        clean_title = re.sub(r'^\d+-\d+강\)\s*', '', clean_title)
        clean_title = re.sub(r'^[a-zA-Z가-힣0-9\s]+강\)\s*', '', clean_title)
        clean_title = clean_title.split(' (')[0].strip()
        
        lec_body = "\n".join(lines[1:])
        
        concept_match = re.search(r'핵심 비즈니스 개념 \(Concept\)[:* ]*(.*)', lec_body)
        concept = concept_match.group(1).strip() if concept_match else ""
        
        apply_match = re.search(r'내 비즈니스 벤치마킹 적용 방안[:* ]*(.*)', lec_body)
        apply_val = apply_match.group(1).strip() if apply_match else ""
        
        flow_match = re.search(r'시스템 구성도 및 데이터 흐름[:* ]*(.*)', lec_body)
        flow = flow_match.group(1).strip() if flow_match else ""
        
        details_map[clean_title] = {
            "concept": concept,
            "apply": apply_val,
            "flow": flow
        }
        
    cat_folder = cat_folders[chapter_num]
    dir_path = str(RESEARCH_COIN_DIR / 'digitalnomad' / '레거시(디지털노마드)' / '대본' / cat_folder)
    
    # Rebuild headers and Table of Contents dynamically to be 100% correct
    title_map = {
        1: "01 블로그 및 애드센스 자동화 실전 마스터 교본",
        2: "02 AI 에이전트 및 프롬프트 실전 마스터 교본",
        3: "03 유튜브 및 영상 음악 자동화 실전 마스터 교본",
        4: "04 AI 이미지 생성 실전 마스터 교본",
        5: "05 수익인증 및 비즈니스 트렌드 실전 마스터 교본"
    }
    
    playlist_url_match = re.search(r'👉 \*\*\[🔗 분야별 유튜브 플레이리스트 \(순서대로 보기\) 클릭\]\((.*?)\)\*', benchmark_content)
    playlist_url = playlist_url_match.group(1) if playlist_url_match else ""
    
    new_content = f"# 📖 {title_map[chapter_num]}\n\n"
    new_content += "이 교본은 **디지털노마드** 채널의 영상을 주제별, 순서별로 하나씩 따라 하며 나만의 자동화 시스템을 구축할 수 있도록 설계된 실전 가이드라인입니다.\n\n"
    if playlist_url:
        new_content += f"> ### 🔗 [분야별 전용 유튜브 플레이리스트 (순서대로 보기) 클릭]({playlist_url})\n"
        new_content += f"> 위 링크를 클릭하시면 본 카테고리의 영상 {len(video_list)}개가 순서대로 재생목록으로 구성되어 바로 시청하실 수 있습니다! 🚀\n\n"
        
    new_content += "## 📌 학습 로드맵 및 목차\n\n"
    for idx, (date, title, url) in enumerate(video_list, 1):
        new_content += f"{idx}. **[{date}]** {title} (🔗 [영상 보기]({url}))\n"
    
    new_content += "\n---\n\n## 📝 영상별 핵심 대본 및 상세 분석\n\n"
    
    # Loop videos and build contents
    for idx, (date, title, url) in enumerate(video_list, 1):
        clean_title = re.sub(r'\(멤버십전용\)|\(멤버십 전용\)|\(마감\)|\(노편집 무자막\)|\(선착순.*?\)', '', title).strip()
        
        unique_info = None
        clean_target = re.sub(r'[^a-zA-Z0-9가-힣]', '', clean_title).lower()
        for t, info in details_map.items():
            clean_t = re.sub(r'[^a-zA-Z0-9가-힣]', '', t).lower()
            if clean_target in clean_t or clean_t in clean_target:
                unique_info = info
                break
                
        concept = unique_info["concept"] if unique_info else "수익 자동화 및 비즈니스 모델 구축 전략."
        apply_val = unique_info["apply"] if unique_info else "동영상 속 기법을 적용한 실전 시스템 구축."
        flow = unique_info["flow"] if unique_info else "수집 ➡️ 가공 ➡️ 발행."
        
        # Load transcript sentences to extract details and tools
        transcript_text = ""
        date_clean = re.sub(r'\D', '', date)
        detected_tools = []
        
        if os.path.exists(dir_path) and len(date_clean) >= 8:
            yymmdd = date_clean[2:8]
            prefix = f"({yymmdd})"
            for f in os.listdir(dir_path):
                if f.startswith(prefix) and f.endswith(".txt"):
                    try:
                        with open(os.path.join(dir_path, f), 'r', encoding='utf-8') as sf:
                            transcript_text = sf.read()
                    except Exception as e:
                        print(f"Error reading transcript {f}: {e}")
                    break
                    
        # Detect tools dynamically from transcript and title
        text_for_detection = (transcript_text + " " + clean_title).lower()
        for t, keywords in TOOLS_INFO.items():
            for kw in keywords:
                if kw.lower() in text_for_detection:
                    if t not in detected_tools:
                        detected_tools.append(t)
                        break
                        
        # Determine topic and custom subheading titles
        topic, short_action, main_sec, sub_sec, sub_text, sub_img, sub_traffic = get_topic_info(clean_title, transcript_text)
        
        # Split transcript sentences
        sentences = []
        if transcript_text:
            sentences = re.split(r'[\.\?\!\n]+', transcript_text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            
        # Group sentences by category
        text_keywords = ["글자", "텍스트", "대본", "가사", "프롬프트", "설정", "config", "json", "입력", "작성", "기획", "키워드", "제목", "주제", "가입", "계정", "설명", "메뉴", "클릭", "저장", "옵션", "기본", "이름", "주소", "선택", "설치", "다운로드", "폴더"]
        img_keywords = ["그림", "사진", "이미지", "미드저니", "감마", "동영상", "영상", "음악", "suno", "수노", "노래", "음원", "화면", "배경", "일러스트", "디자인", "스킨", "테마", "자막", "편집", "캡컷", "vrew", "브루", "움직임", "모션", "플레이리스트", "보컬", "음색", "카메라", "촬영", "프레임"]
        traffic_keywords = ["유입", "트래픽", "외부", "링크", "지식인", "지식in", "스레드", "threads", "서치", "콘솔", "웹마스터", "네이버", "다음", "구글", "등록", "제출", "사이트맵", "rss", "수집", "텔레그램", "알림", "메신저", "공유", "수익", "애드센스", "승인", "광고", "배포", "홍보", "주소창", "도메인", "가비아"]

        text_sents = []
        img_sents = []
        traffic_sents = []
        
        for s in sentences:
            s_lower = s.lower()
            t_score = sum(1 for kw in text_keywords if kw in s_lower)
            i_score = sum(1 for kw in img_keywords if kw in s_lower)
            tr_score = sum(1 for kw in traffic_keywords if kw in s_lower)
            
            max_score = max(t_score, i_score, tr_score)
            if max_score == 0:
                continue
                
            if max_score == t_score:
                text_sents.append(s)
            elif max_score == i_score:
                img_sents.append(s)
            else:
                traffic_sents.append(s)
                
        # Get action steps for each subsection
        def get_action_steps(cat_sents):
            matched = []
            for s in cat_sents:
                s_clean = s.strip()
                if len(s_clean) < 15 or len(s_clean) > 120:
                    continue
                if any(m[:15] == s_clean[:15] for m in matched):
                    continue
                matched.append(s_clean)
            return matched[:3]

        text_steps_extracted = get_action_steps(text_sents)
        img_steps_extracted = get_action_steps(img_sents)
        traffic_steps_extracted = get_action_steps(traffic_sents)
        
        # Categorize detected tools
        text_tools_list = ["고수익 황금 키워드", "고수익 멘토", "꿀제목 생성기", "스타일러 프로", "Claude AI (MCP)", "GPT-4o / ChatGPT", "ElevenLabs", "Suno AI", "Vrew"]
        img_tools_list = ["감마AI", "미드저니", "캡컷", "디노 5.5"]
        traffic_tools_list = ["스레드 만능 생성기", "디노 지식인 봇", "유튜브 API", "텔레그램 봇 API", "쿠팡 파트너스", "네이버 쇼핑커넥트", "블로그스팟", "워드프레스", "티스토리", "구글 서치 콘솔", "네이버 서치 어드바이저", "빙 웹마스터 도구", "다음 웹마스터 도구", "구글 애드센스"]
        
        text_bullets = []
        img_bullets = []
        traffic_bullets = []
        
        for t in detected_tools:
            bullet = get_tool_bullet(t, topic, sentences)
            if t in text_tools_list:
                text_bullets.append(bullet)
            elif t in img_tools_list:
                img_bullets.append(bullet)
            elif t in traffic_tools_list:
                traffic_bullets.append(bullet)
            else:
                # heuristic fallback
                if "키워드" in t or "멘토" in t or "제목" in t or "프롬프트" in t or "claude" in t.lower() or "gpt" in t.lower():
                    text_bullets.append(bullet)
                elif "이미지" in t or "그림" in t or "디자인" in t or "영상" in t or "편집" in t:
                    img_bullets.append(bullet)
                else:
                    traffic_bullets.append(bullet)
                    
        # Jargon clean concept, apply, flow
        clean_concept = clean_jargon(concept)
        clean_apply = clean_jargon(apply_val)
        clean_flow = clean_jargon(flow)
        
        # Format subsections output
        def format_section_content(bullets, extracted_sents, default_action_desc):
            lines = []
            if bullets:
                lines.extend(bullets)
            if extracted_sents:
                lines.append("* **실전 실행 단계**:")
                for es in extracted_sents:
                    lines.append(f"  * {clean_jargon(es)}")
            if not bullets and not extracted_sents:
                lines.append(f"- {default_action_desc}")
            return "\n".join(lines)

        text_section_output = format_section_content(text_bullets, text_steps_extracted, "주제 선정 및 관련 대본/설정 데이터를 기획하여 글쓰기를 준비합니다.")
        img_section_output = format_section_content(img_bullets, img_steps_extracted, "콘텐츠 내용에 어울리는 영상, 음악, 디자인 요소 등의 미디어를 구성하여 본문을 완성합니다.")
        traffic_section_output = format_section_content(traffic_bullets, traffic_steps_extracted, "검색 등록 및 추천 링크 삽입 등을 통해 외부에서 방문자가 유입되도록 연결합니다.")
        
        # Custom "꿀팁" box under Subsection 1
        tip_desc = get_topic_tip(topic, clean_title)
        tip_box_html = (
            f"<div style='background-color: #fffbeb; border-left: 4px solid #d97706; padding: 10px 15px; border-radius: 4px; margin: 10px 0; color: #b45309; font-weight: 600;'>\n"
            f"  💡 꿀팁: {tip_desc}\n"
            f"</div>"
        )
        
        # Build tool display string
        tools_str = ""
        if detected_tools:
            tools_str = " ".join(make_html_tool(t) for t in detected_tools)
        else:
            tools_str = '<span style="color: #64748b; font-size: 0.9em; font-style: italic;">검출된 전용 자동화 도구 없음 (개별 단계 진행)</span>'
            
        # Write headings and box details
        lec_num_str = f"{chapter_num}-{idx}강) {short_action} ({clean_title})"
        
        new_content += f"### 📍 {lec_num_str}\n"
        new_content += (
            f"<div style='background-color: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 12px; padding: 20px; margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);'>\n"
            f"  <div style='margin-bottom: 15px; display: flex; align-items: center; gap: 10px;'>\n"
            f"    <span style='background-color: #e0f2fe; color: #0369a1; padding: 6px 12px; border-radius: 20px; font-size: 0.9em; font-weight: 800; border: 1px solid #bae6fd;'>📅 업로드 일자: {date}</span>\n"
            f"    <a href='{url}' style='background-color: #fee2e2; color: #dc2626; padding: 6px 12px; border-radius: 20px; font-size: 0.9em; font-weight: 800; text-decoration: none;'>📺 영상 바로가기</a>\n"
            f"  </div>\n"
            f"  <div style='margin-top: 15px; padding: 12px 15px; background-color: #ffffff; border-radius: 8px; border: 1px dashed #cbd5e1;'>\n"
            f"    <strong style='color: #0f172a; font-size: 1.05em; display: block; margin-bottom: 8px;'>🛠️ 사용 도구 (TOOL LIST)</strong>\n"
            f"    {tools_str}\n"
            f"  </div>\n"
            f"</div>\n\n"
        )
        
        new_content += f"### 🧱 [1] {main_sec}\n\n"
        new_content += f"#### ✍️ (1) {sub_text}\n"
        new_content += f"{text_section_output}\n\n"
        # Insert the custom 꿀팁 box here
        new_content += f"{tip_box_html}\n\n"
        new_content += f"#### 🖼️ (2) {sub_img}\n"
        new_content += f"{img_section_output}\n\n"
        
        new_content += f"### 🚀 [2] {sub_sec}\n\n"
        new_content += f"#### 🔗 (1) {sub_traffic}\n"
        new_content += f"{traffic_section_output}\n\n"
        
        # Build bottom Hacks Box
        hacks_box = (
            f"<div style='background-color: #f0fdf4; border-left: 5px solid #16a34a; padding: 18px; border-radius: 8px; margin: 25px 0;'>\n"
            f"  <strong style='color: #15803d; font-size: 1.1em; display: block; margin-bottom: 10px;'>💡 [꿀팁]</strong>\n"
            f"  <span style='color: #166534; font-weight: 500; line-height: 1.7;'>\n"
            f"    <strong>🎯 핵심 요약:</strong> {clean_concept}<br>\n"
            f"    <strong>⚙️ 벤치마킹 적용:</strong> {clean_apply}<br>\n"
            f"    <strong>🔄 작업 순서:</strong> {clean_flow}\n"
            f"  </span>\n"
            f"</div>"
        )
        new_content += f"{hacks_box}\n\n"
        new_content += "---\n\n"
        
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Updated Markdown Book: {md_path}")
    
    # Generate PDF
    pdf_filename = md_filename.replace('.md', '.pdf')
    pdf_path = os.path.join(book_dir, pdf_filename)
    
    temp_html = md_path.replace('.md', '_temp.html')
    html_content = markdown.markdown(new_content, extensions=['fenced_code', 'tables'])
    
    premium_html = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{md_filename}</title>
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Noto+Sans+KR:wght@400;700;900&display=swap');
        body {{
            font-family: 'Noto Sans KR', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.8;
            color: #334155;
            margin: 40px;
        }}
        h1 {{
            font-size: 26pt;
            font-weight: 900;
            color: #1e1b4b;
            border-bottom: 3px solid #4f46e5;
            padding-bottom: 12px;
            margin-top: 0;
            margin-bottom: 30px;
            text-align: center;
        }}
        h2 {{
            font-size: 20pt;
            font-weight: 900;
            color: #312e81;
            margin-top: 50px;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 8px;
        }}
        h3 {{
            font-size: 15pt;
            font-weight: 900;
            color: #1e1b4b;
            margin-top: 50px;
            border-left: 6px solid #4f46e5;
            padding-left: 12px;
            margin-bottom: 20px;
            page-break-before: always;
        }}
        h4 {{
            font-size: 13pt;
            font-weight: 800;
            color: #0f172a;
            margin-top: 25px;
            margin-bottom: 8px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 4px;
        }}
        h5 {{
            font-size: 11pt;
            font-weight: 700;
            color: #4f46e5;
            margin-top: 15px;
            margin-bottom: 5px;
        }}
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        ul, ol {{
            padding-left: 25px;
            margin-bottom: 15px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        code {{
            font-family: inherit;
        }}
        @media print {{
            body {{ margin: 0; }}
        }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(premium_html)
        
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    try:
        abs_html_path = os.path.abspath(temp_html)
        url = f"file:///{abs_html_path.replace(os.sep, '/')}"
        driver.get(url)
        driver.implicitly_wait(2)
        print_options = {
            'landscape': False,
            'displayHeaderFooter': False,
            'printBackground': True,
            'preferCSSPageSize': True
        }
        pdf_data = driver.execute_cdp_cmd("Page.printToPDF", print_options)
        with open(pdf_path, 'wb') as f:
            f.write(base64.b64decode(pdf_data['data']))
        print(f"Generated PDF Book for: {pdf_filename}")
    except Exception as e:
        print(f"Failed to generate PDF Book: {e}")
    finally:
        driver.quit()
        if os.path.exists(temp_html):
            os.remove(temp_html)

if __name__ == "__main__":
    for md_filename, benchmark_filename, chap_num in categories:
        rewrite_book_from_benchmark(md_filename, benchmark_filename, chap_num)
    print("\nAll books successfully rebuilt in dynamic jargon-free format!")
