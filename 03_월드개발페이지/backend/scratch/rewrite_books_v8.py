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

def extract_details(title, chapter_num, concept, apply_val, flow):
    title_lower = title.lower()
    detected_tools = []
    
    # Keyword tool detection
    if "멘토" in title_lower:
        detected_tools.append("고수익 멘토")
    if "키워드" in title_lower or "황금" in title_lower:
        detected_tools.append("고수익 황금 키워드")
    if "제목" in title_lower:
        detected_tools.append("꿀제목 생성기")
    if "스타일러" in title_lower or "styler" in title_lower:
        detected_tools.append("스타일러 프로")
    if "감마" in title_lower or "gamma" in title_lower:
        detected_tools.append("감마AI")
    if "미드저니" in title_lower or "midjourney" in title_lower:
        detected_tools.append("미드저니")
    if "스레드" in title_lower or "thread" in title_lower:
        detected_tools.append("스레드 만능 생성기")
    if "지식인" in title_lower or "지식in" in title_lower:
        detected_tools.append("디노 지식인 봇")
    if "클로드" in title_lower or "claude" in title_lower or "mcp" in title_lower:
        detected_tools.append("Claude AI (MCP)")
    if "suno" in title_lower or "수노" in title_lower:
        detected_tools.append("Suno AI")
    if "유튜브" in title_lower or "플레이리스트" in title_lower:
        detected_tools.append("유튜브 API")
    if "쿠팡" in title_lower or "쿠파스" in title_lower:
        detected_tools.append("쿠팡 파트너스")
        
    # Apply category defaults to ensure robust toolset coverage
    if chapter_num == 1:
        defaults = ["고수익 황금 키워드", "고수익 멘토", "감마AI", "미드저니", "스타일러 프로"]
    elif chapter_num == 2:
        defaults = ["Claude AI (MCP)", "GPT-4o / ChatGPT", "스타일러 프로"]
    elif chapter_num == 3:
        defaults = ["유튜브 API", "Suno AI", "미드저니", "ElevenLabs"]
    elif chapter_num == 4:
        defaults = ["미드저니", "스타일러 프로"]
    else:
        defaults = ["고수익 황금 키워드", "디노 지식인 봇", "쿠팡 파트너스", "스레드 만능 생성기"]
        
    for d in defaults:
        if d not in detected_tools:
            detected_tools.append(d)
            
    tools_str = " ".join(make_html_tool(t) for t in detected_tools)
    
    # Determine Short Action Name
    short_action = "자동화 블로그 작업"
    if "에이전트" in title or "mcp" in title.lower():
        short_action = "AI 에이전트 개발"
    elif "플레이리스트" in title or "음악" in title or "유튜브" in title or "suno" in title.lower():
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
        
    clean_concept = clean_jargon(concept)
    clean_apply = clean_jargon(apply_val)
    clean_flow = clean_jargon(flow)
    
    # Build clean conceptual summaries for each category using jargon-free terms
    if chapter_num == 1:
        text_steps = (
            f"- {make_html_tool('고수익 황금 키워드')} : 사람들이 검색하는 고단가 주제를 발굴하고 조회수와 단가를 분석하여 핵심 키워드를 찾습니다.\n"
            f"- {make_html_tool('고수익 멘토')} : 메인 주제와 보조 주제를 나누어 배치하고, 서브 글들이 메인 글의 노출을 든든히 밀어주도록 목차 구조를 설계합니다.\n"
            f"- 만약 유입이 적다면, 즉각 {make_html_tool('꿀제목 생성기')}를 사용하여 누르고 싶어지는 매력적인 제목으로 교체합니다."
        )
        image_steps = (
            f"- {make_html_tool('감마AI')} : 글의 개요나 목차를 복사해 넣고, 문단별로 어울리는 카드 형태의 설명 이미지를 한 번에 만들어 냅니다.\n"
            f"- {make_html_tool('미드저니')} : 문단 수에 맞게 필요한 이미지(예: 7개 문단인 경우 28장)를 생성하여, 중복되지 않는 그림으로 문단당 3장씩 배치해 방문자가 머무는 시간을 늘립니다."
        )
        traffic_steps = (
            f"- **네이버 지식IN 활용** : 작성한 글의 링크 주소를 지식인 답변 버튼에 자연스럽게 삽입하여 실시간 방문자를 당깁니다.\n"
            f"- {make_html_tool('스레드 만능 생성기')} : 주소를 단축하여 스레드 계정에 자동으로 글을 올려 외부 방문자 통로를 확보합니다."
        )
        hacks = (
            f"이번 공부의 핵심 원리는 다음과 같습니다: **{clean_concept}**\n\n"
            f"실전에 바로 적용하려면 **{clean_apply}** 방식을 채택하는 것이 좋습니다. "
            f"방문자가 내 블로그에 오래 머무르도록 독창적인 글을 쓰고, 적절한 위치에 그림을 배치하는 것이 비결입니다."
        )
        
    elif chapter_num == 2:
        text_steps = (
            f"- {make_html_tool('Claude AI (MCP)')} : 내 컴퓨터의 파일 작업과 자동화 명령을 스스로 내리는 지능형 비서 환경을 설정합니다.\n"
            f"- {make_html_tool('GPT-4o / ChatGPT')} : 비서에게 역할을 명확히 부여하고, 예시와 제약 조건을 준수한 명령문을 만들어 원고 작성을 자동화합니다."
        )
        image_steps = (
            f"- {make_html_tool('감마AI')} : 작동 흐름이나 시스템 구조를 시각화한 설명 카드를 작성합니다.\n"
            f"- {make_html_tool('미드저니')} : 프로그램의 화면 구성이나 메뉴 버튼에 사용할 디자인 이미지를 일괄 생성합니다."
        )
        traffic_steps = (
            f"- **지식인 연계** : 질문에 대한 답변과 함께 내가 만든 자동화 비서 소개 링크를 넣어 방문자를 확보합니다.\n"
            f"- {make_html_tool('스레드 만능 생성기')} : 프로그램 다운로드 주소를 단축하여 스레드에 정기적으로 소식을 전해 사용자를 모읍니다."
        )
        hacks = (
            f"이번 공부의 핵심 원리는 다음과 같습니다: **{clean_concept}**\n\n"
            f"실전에 바로 적용하려면 **{clean_apply}** 방식을 채택하는 것이 좋습니다. "
            f"자동화 프로그램이 오작동 없이 작동하도록 명령어의 규칙을 촘촘히 짜고 오류를 검증하는 절차를 밟는 것이 비결입니다."
        )
        
    elif chapter_num == 3:
        text_steps = (
            f"- {make_html_tool('GPT-4o / ChatGPT')} : 영상에 들어갈 감성적인 노래 제목, 아티스트 정보 및 음악 장르 분류를 기획합니다.\n"
            f"- {make_html_tool('유튜브 API')} : 유튜브 검색 결과 상위에 노출될 수 있도록 제목과 영상 상세 정보란에 적합한 단어들을 배치합니다."
        )
        image_steps = (
            f"- {make_html_tool('미드저니')} : 음악 감상 영상의 배경이 될 감성적이고 몰입감 있는 배경 이미지를 최적 화면 비율에 맞춰 생성합니다.\n"
            f"- {make_html_tool('감마AI')} : 노래 리스트 구성 및 관련 정보 카드를 깔끔한 프레젠테이션 디자인으로 가공합니다."
        )
        traffic_steps = (
            f"- **유튜브 추천 경로 활용** : 추천 동영상 연동 및 고정 댓글에 2차 이동 링크 버튼을 달아 방문자를 유입시킵니다.\n"
            f"- {make_html_tool('스레드 만능 생성기')} : 쇼츠나 짧은 미리보기 영상을 스레드에 업로드하고 단축 링크를 엮어 방문 트래픽을 당깁니다."
        )
        hacks = (
            f"이번 공부의 핵심 원리는 다음과 같습니다: **{clean_concept}**\n\n"
            f"실전에 바로 적용하려면 **{clean_apply}** 방식을 채택하는 것이 좋습니다. "
            f"귀에 편안한 무료/라이센스 음원을 매크로 프로그램으로 결합하고 미드저니의 예술적 이미지를 얹어 최상의 콘텐츠를 대량 생산하는 것이 비결입니다."
        )
        
    elif chapter_num == 4:
        text_steps = (
            f"- {make_html_tool('GPT-4o / ChatGPT')} : 미드저니가 이해하기 쉬운 상세한 묘사와 카메라 설정 명령을 영어로 보강합니다.\n"
            f"- {make_html_tool('스타일러 프로')} : 대량으로 이미지를 뽑아낼 때 필요한 테마별 분류와 사진 설명 텍스트를 기획합니다."
        )
        image_steps = (
            f"- {make_html_tool('미드저니')} : 동일한 그림체와 컨셉이 깨지지 않는 모델 사진 및 고품질 풍경 사진들을 비율별로 일괄 양산합니다.\n"
            f"- {make_html_tool('감마AI')} : 생성된 이미지 작품집과 다운로드 판매용 쇼룸 웹페이지를 템플릿 카드로 일괄 구축합니다."
        )
        traffic_steps = (
            f"- **이미지 거래 플랫폼 활용** : 상업적 이미지 판매 사이트 버튼 링크를 연동하고 핀터레스트 등에 자동 핀을 연결하여 판매로 이끕니다.\n"
            f"- {make_html_tool('스레드 만능 생성기')} : 고품질 월페이퍼 무료 배포 단축 주소 링크를 스레드에 업로드하여 팔로워를 모읍니다."
        )
        hacks = (
            f"이번 공부의 핵심 원리는 다음과 같습니다: **{clean_concept}**\n\n"
            f"실전에 바로 적용하려면 **{clean_apply}** 방식을 채택하는 것이 좋습니다. "
            f"동일 인물의 다양한 포즈를 일관되게 추출하고 화질을 깨끗하게 확대하는 가공 작업이 상품성을 결정짓는 비결입니다."
        )
        
    else: # chapter_num == 5
        text_steps = (
            f"- {make_html_tool('고수익 황금 키워드')} : 현재 소비자들이 많이 검색하는 인기 있는 추천 상품 키워드를 발굴합니다.\n"
            f"- {make_html_tool('고수익 멘토')} : 물건을 사는 사람들의 구매 심리를 자극하고 정보 신뢰성을 주는 메인/서브 글 구조를 설계합니다.\n"
            f"- {make_html_tool('스타일러 프로')} : 상품 비교 및 진정성 있는 후기 형태의 양질의 글을 자동으로 생성합니다."
        )
        image_steps = (
            f"- {make_html_tool('감마AI')} : 제품 비교 표나 특징 분석 그래픽 카드를 설명 슬라이드 형태로 고속 제작합니다.\n"
            f"- {make_html_tool('미드저니')} : 상품 사용 가상 컷 및 홍보용 라이프스타일 이미지를 컨셉별로 일괄 양산합니다."
        )
        traffic_steps = (
            f"- {make_html_tool('디노 지식인 봇')} : 지식인 질문 글에 답변을 제공하며 우회 추천용 이동 버튼 링크를 삽입해 방문자를 당깁니다.\n"
            f"- {make_html_tool('스레드 만능 생성기')} : 홍보 링크를 단축 링크로 변환하여 스레드에 올려 방문자를 극대화합니다."
        )
        hacks = (
            f"이번 공부의 핵심 원리는 다음과 같습니다: **{clean_concept}**\n\n"
            f"실전에 바로 적용하려면 **{clean_apply}** 방식을 채택하는 것이 좋습니다. "
            f"광고 링크를 중간에 우회하는 중간 다리 블로그를 활용하여 검색 사이트의 규제를 피하고 안정적으로 연금 수입을 구축하는 것이 비결입니다."
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

    return short_action, tools_str, text_steps, image_steps, traffic_steps, hacks_box

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
    
    # Split the benchmark file into lectures to get individual concept blocks
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
        
        # Look up unique details
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
        
        short_action, tools_str, text_steps, image_steps, traffic_steps, hacks = extract_details(clean_title, chapter_num, concept, apply_val, flow)
        
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
        
        new_content += f"#### 🏗️ [1] {short_action} 내용완성\n\n"
        new_content += f"##### ✍️ (1) 글자\n"
        new_content += f"{text_steps}\n\n"
        new_content += f"##### 🖼️ (2) 그림\n"
        new_content += f"{image_steps}\n\n"
        
        new_content += f"#### 🔗 [2] 부가작업\n\n"
        new_content += f"##### 🚀 (1) 트래픽 유입(백링크작업)\n"
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
    print("All books successfully rebuilt in clean conceptual format with zero jargon!")
