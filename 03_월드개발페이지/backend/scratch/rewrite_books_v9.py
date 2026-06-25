import os
import re
import base64
import markdown
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

book_dir = "coin/digitalnomad/책"

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
    "텔레그램 봇 API": ["텔레그램", "telegram"]
}

def make_html_tool(name):
    return f'<span style="background-color: #eff6ff; color: #1d4ed8; padding: 4px 8px; border-radius: 6px; font-weight: bold; border: 1px solid #bfdbfe; font-size: 0.85em; display: inline-block; margin: 2px;">[T] {name}</span>'

def clean_jargon(text):
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
        "데이터베이스": "저장소"
    }
    for eng, kor in replacements.items():
        text = re.sub(re.escape(eng), kor, text, flags=re.IGNORECASE)
    return text

def get_original_title(category_num, upload_date):
    cat_folder = cat_folders[category_num]
    dir_path = f"coin/digitalnomad/레거시(디지털노마드)/대본/{cat_folder}"
    if os.path.exists(dir_path):
        date_clean = re.sub(r'\D', '', upload_date)
        if len(date_clean) >= 8:
            yymmdd = date_clean[2:8]
            prefix = f"({yymmdd})"
            for f in os.listdir(dir_path):
                if f.startswith(prefix) and f.endswith(".txt"):
                    orig_title = f[len(prefix):]
                    orig_title = re.sub(r'\.txt$', '', orig_title).strip()
                    return orig_title
    return None

def detect_tools_from_transcript(category_num, upload_date, title):
    cat_folder = cat_folders[category_num]
    dir_path = f"coin/digitalnomad/레거시(디지털노마드)/대본/{cat_folder}"
    detected = []
    
    title_lower = title.lower()
    for tool, keywords in TOOLS_INFO.items():
        for kw in keywords:
            if kw.lower() in title_lower:
                if tool not in detected:
                    detected.append(tool)
                    break
                    
    if os.path.exists(dir_path):
        date_clean = re.sub(r'\D', '', upload_date)
        if len(date_clean) >= 8:
            yymmdd = date_clean[2:8]
            prefix = f"({yymmdd})"
            for f in os.listdir(dir_path):
                if f.startswith(prefix) and f.endswith(".txt"):
                    with open(os.path.join(dir_path, f), 'r', encoding='utf-8') as sf:
                        text = sf.read().lower()
                        for tool, keywords in TOOLS_INFO.items():
                            for kw in keywords:
                                if kw.lower() in text:
                                    if tool not in detected:
                                        detected.append(tool)
                                        break
    return detected

def generate_custom_bullet_points(detected_tools):
    tool_actions = {
        "고수익 황금 키워드": "사람들이 검색하는 단어 중 클릭했을 때 수익 가격이 높은 핵심 키워드를 선별하고 발굴합니다.",
        "고수익 멘토": "메인 키워드와 보조 키워드의 계층 구조를 짜서 내부 추천 링크 연결 흐름을 설계합니다.",
        "꿀제목 생성기": "방문자의 호기심을 유발하여 높은 클릭율을 이끌어내는 후킹용 제목을 만듭니다.",
        "스타일러 프로": "대주제와 소주제에 맞춘 양질의 블로그용 원고 본문을 한 번에 대량으로 작성합니다.",
        "감마AI": "목차와 개요를 바탕으로 본문에 어울리는 설명 카드와 프레젠테이션 디자인을 구성합니다.",
        "미드저니": "글의 주제와 컨셉에 맞는 개성 있는 고품질 이미지를 최적의 가로세로 비율로 생성합니다.",
        "스레드 만능 생성기": "홍보용 링크 주소를 가공하여 스레드 등의 소셜 미디어에 자동으로 글을 올립니다.",
        "디노 지식인 봇": "네이버 지식인 질문글에 유용한 답변을 달고 버튼식 링크 주소를 연계하여 방문자를 당깁니다.",
        "Claude AI (MCP)": "컴퓨터 파일 관리와 프로그램 작성을 처리할 수 있도록 가상 비서 환경을 설정합니다.",
        "Suno AI": "기획한 장르와 분위기에 맞는 인공지능 음악을 작곡하여 노래 음원을 제작합니다.",
        "GPT-4o / ChatGPT": "특정 대화 전문가 역할을 부여하여 감성적인 본문 글이나 영상 설명 대본을 작성합니다.",
        "블로그스팟": "구글 블로그스팟 사이트의 스킨과 기본 글 작성을 간편하게 설정합니다.",
        "워드프레스": "워드프레스 블로그 사이트에 자동 업로드 연동 환경을 구축합니다.",
        "티스토리": "티스토리 블로그의 HTML 편집 모드를 활용해 스킨 및 내부 링크 버튼을 세팅합니다.",
        "쿠팡 파트너스": "제품 정보와 연동되는 추천 링크 코드를 발굴하여 수익 링크를 삽입합니다.",
        "네이버 쇼핑커넥트": "네이버 쇼핑 상품 정보와 가격 데이터를 조회하여 비교 리뷰용 원고를 준비합니다.",
        "유튜브 API": "영상의 제목과 상세 정보, 검색 단어 목록을 유튜브 사이트에 자동으로 올립니다.",
        "yt-dlp": "유튜브 동영상의 한글 자막 정보와 오디오 원본 파일을 빠르게 내려받습니다.",
        "캡컷": "미리 구성된 영상 틀과 간편 편집 기능을 활용해 읽기 쉬운 자막 모양을 입힙니다.",
        "Vrew": "자동 음성 분석 기능을 사용해 동영상 속 목소리 시점에 어울리는 자막을 추출합니다.",
        "ElevenLabs": "자연스러운 목소리 톤의 인공지능 음성 파일을 캐릭터별로 생성합니다.",
        "텔레그램 봇 API": "블로그 발행 성공 여부나 실시간 방문자 유입 상태를 메신저 알림으로 실시간 전송합니다."
    }
    
    text_bullets = []
    img_bullets = []
    traffic_bullets = []
    
    text_tools = ["고수익 황금 키워드", "고수익 멘토", "꿀제목 생성기", "스타일러 프로", "Claude AI (MCP)", "GPT-4o / ChatGPT", "ElevenLabs", "Suno AI", "Vrew"]
    img_tools = ["감마AI", "미드저니", "캡컷"]
    traffic_tools = ["스레드 만능 생성기", "디노 지식인 봇", "유튜브 API", "텔레그램 봇 API", "쿠팡 파트너스", "네이버 쇼핑커넥트", "블로그스팟", "워드프레스", "티스토리"]
    
    for t in detected_tools:
        action = tool_actions.get(t, "관련 작업을 자동으로 처리합니다.")
        bullet = f"- {make_html_tool(t)} : {action}"
        if t in text_tools:
            text_bullets.append(bullet)
        elif t in img_tools:
            img_bullets.append(bullet)
        elif t in traffic_tools:
            traffic_bullets.append(bullet)
        else:
            if "키워드" in t or "멘토" in t or "제목" in t or "프로" in t or "ai" in t.lower() or "chat" in t.lower():
                text_bullets.append(bullet)
            elif "이미지" in t or "그림" in t or "디자인" in t:
                img_bullets.append(bullet)
            else:
                traffic_bullets.append(bullet)
                
    if not text_bullets:
        text_bullets.append("- 작업에 필요한 글자 작성 및 원고 정리 단계를 진행합니다.")
    if not img_bullets:
        img_bullets.append("- 영상/글에 필요한 배경 화면 및 디자인 리소스를 배치합니다.")
    if not traffic_bullets:
        traffic_bullets.append("- 외부 통로를 만들어 방문자가 모이도록 유입 경로를 연결합니다.")
        
    return "\n".join(text_bullets), "\n".join(img_bullets), "\n".join(traffic_bullets)

def extract_details_v2(title, chapter_num, concept, apply_val, flow, detected_tools):
    title_lower = title.lower()
    
    # 1. Determine Short Action Name
    short_action = "자동화 블로그 작업"
    if "에이전트" in title or "mcp" in title_lower:
        short_action = "AI 에이전트 개발"
    elif "플레이리스트" in title or "음악" in title or "유튜브" in title or "suno" in title_lower:
        short_action = "유튜브 영상 자동화"
    elif "이미지" in title:
        short_action = "AI 이미지 양산"
    elif "지식인" in title or "트래픽" in title or "외부유입" in title:
        short_action = "트래픽 외부유입 작업"
    elif "티스토리" in title:
        short_action = "티스토리 작업"
    elif "워드프레스" in title:
        short_action = "워드프레스 작업"
    elif "승인" in title:
        short_action = "애드센스 승인 작업"
    elif "수익" in title or "인증" in title:
        short_action = "수익 자동화 설계"
        
    # 2. Determine Subheading Titles
    if chapter_num == 1 or chapter_num == 5:
        main_sec_name = f"{short_action} 내용완성"
        sub_sec_name = f"{short_action} 부가작업"
        text_title = "글자"
        img_title = "그림"
        traffic_title = "트래픽 유입(백링크작업)"
    elif chapter_num == 2:
        main_sec_name = f"{short_action} 환경구축"
        sub_sec_name = f"{short_action} 자동 실행"
        text_title = "명령어 및 코드 작성"
        img_title = "작동 환경 설정"
        traffic_title = "작동 결과 모니터링"
    elif chapter_num == 3:
        main_sec_name = f"{short_action} 영상완성"
        sub_sec_name = f"{short_action} 부가작업"
        text_title = "음원 및 대본"
        img_title = "영상 및 썸네일"
        traffic_title = "유튜브 채널 등록 및 홍보"
    elif chapter_num == 4:
        main_sec_name = f"{short_action} 이미지완성"
        sub_sec_name = f"{short_action} 부가작업"
        text_title = "명령어 설계"
        img_title = "사진 출력 및 가공"
        traffic_title = "거래 사이트 업로드 및 판매"
    else:
        main_sec_name = "콘텐츠완성"
        sub_sec_name = "부가작업"
        text_title = "글자"
        img_title = "그림"
        traffic_title = "방문 유도 링크 연결"

    # Translate jargon
    clean_concept = clean_jargon(concept)
    clean_apply = clean_jargon(apply_val)
    clean_flow = clean_jargon(flow)
    
    # Generate custom bullets based on detected tools
    text_steps, image_steps, traffic_steps = generate_custom_bullet_points(detected_tools)
    
    # Compose hacks without jargon
    hacks = (
        f"이번 강의의 핵심 요점은 다음과 같습니다: **{clean_concept}**\n\n"
        f"실전에 바로 적용하려면 **{clean_apply}**를 핵심으로 두십시오. "
        f"반복적인 수작업을 없애고 도구를 유기적으로 엮어 방문자의 마음을 사로잡는 것이 비결입니다."
    )
    
    hacks_box = (
        f"<div style='background-color: #f0fdf4; border-left: 5px solid #16a34a; padding: 18px; border-radius: 8px; margin: 20px 0;'>\n"
        f"  <strong style='color: #15803d; font-size: 1.1em; display: block; margin-bottom: 10px;'>💡 코다리 부장의 실전 가이드 & 꿀팁</strong>\n"
        f"  <span style='color: #166534; font-weight: 500; line-height: 1.7;'>\n"
        f"    <strong>🔥 실전 핵심 전략:</strong> {hacks}<br><br>\n"
        f"    <strong>⚙️ 작업 순서:</strong> {clean_flow}\n"
        f"  </span>\n"
        f"</div>"
    )
    
    return short_action, main_sec_name, sub_sec_name, text_title, img_title, traffic_title, text_steps, image_steps, traffic_steps, hacks_box

def rewrite_book_from_benchmark(md_filename, benchmark_filename, chapter_num):
    md_path = os.path.join(book_dir, md_filename)
    benchmark_path = os.path.join(book_dir, benchmark_filename)
    
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
        
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    header_match = re.search(r'^(.*?)(### 📍 |\Z)', md_content, re.DOTALL)
    header = header_match.group(1).strip() if header_match else ""
    
    new_content = header + "\n\n"
    new_content += "## 📝 영상별 핵심 대본 및 상세 분석\n\n"
    
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
        
        # Detect tools dynamically from transcript
        detected_tools = detect_tools_from_transcript(chapter_num, date, clean_title)
        
        short_action, main_sec_name, sub_sec_name, text_title, img_title, traffic_title, text_steps, image_steps, traffic_steps, hacks = extract_details_v2(
            clean_title, chapter_num, concept, apply_val, flow, detected_tools
        )
        
        tools_str = " ".join(make_html_tool(t) for t in detected_tools)
        
        # Format heading: Chapter-Lecture강) Action (OriginalTitle)
        lec_num_str = f"{chapter_num}-{idx}강) {short_action} ({clean_title})"
        
        new_content += f"### 📍 {lec_num_str}\n"
        
        new_content += (
            f"<div style='background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin-bottom: 20px;'>\n"
            f"  <div style='margin-bottom: 10px;'>\n"
            f"    <span style='background-color: #f1f5f9; color: #475569; padding: 3px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; margin-right: 10px;'>📅 업로드 일자: {date}</span>\n"
            f"    <a href='{url}' style='background-color: #fee2e2; color: #dc2626; padding: 3px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; text-decoration: none;'>📺 영상 바로가기</a>\n"
            f"  </div>\n"
            f"  <div style='margin-top: 15px;'>\n"
            f"    <strong style='color: #0f172a; font-size: 1em; display: block; margin-bottom: 8px;'>🛠️ 사용 도구 (TOOLS)</strong>\n"
            f"    {tools_str}\n"
            f"  </div>\n"
            f"</div>\n\n"
        )
        
        new_content += f"#### 🏗️ [1] {main_sec_name}\n\n"
        new_content += f"##### ✍️ (1) {text_title}\n"
        new_content += f"{text_steps}\n\n"
        new_content += f"##### 🖼️ (2) {img_title}\n"
        new_content += f"{image_steps}\n\n"
        
        new_content += f"#### 🔗 [2] {sub_sec_name}\n\n"
        new_content += f"##### 🚀 (1) {traffic_title}\n"
        new_content += f"{traffic_steps}\n\n"
        
        new_content += f"#### [꿀팁]\n"
        new_content += f"{hacks}\n\n"
        new_content += "---\n\n"
        
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Updated Markdown Book: {md_path}")
    
    # Generate PDF without jargon
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
    print("All books successfully rebuilt in clean conceptual format with dynamic titles and tools!")
