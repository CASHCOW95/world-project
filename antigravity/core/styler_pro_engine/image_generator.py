import os
import sys
import random
import re
import io
import base64
import json
import urllib.request
import urllib.parse
from pathlib import Path

# Auto-install Pillow if not present
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess
    sys.stderr.write("Pillow not found. Auto-installing Pillow...\n")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        from PIL import Image, ImageDraw, ImageFont
    except Exception as e:
        sys.stderr.write(f"Failed to auto-install Pillow: {str(e)}\n")
        # Fail gracefully by mocking Image operations
        pass

# English slug translator helper for SEO filenames
SEO_TRANSLATION_MAP = {
    "당뇨": "diabetes",
    "환자": "patient",
    "과일": "fruit",
    "음식": "food",
    "혈당": "blood-sugar",
    "가스비": "gas-bill",
    "절약": "save",
    "난방비": "heating-bill",
    "전기세": "electricity-bill",
    "꿀팁": "tips",
    "가이드": "guide",
    "건강": "health",
    "관리": "management",
    "부작용": "side-effects",
    "추천": "recommend",
    "노출": "seo-ranking",
    "수익": "revenue"
}

def make_seo_filename(keyword, img_index):
    # Convert matches in keyword to slugs
    slug_parts = []
    for word, slug in SEO_TRANSLATION_MAP.items():
        if word in keyword:
            slug_parts.append(slug)
            
    if not slug_parts:
        slug_parts.append("blog-post")
        
    slug_parts.append(f"image-{img_index}")
    return f"{'-'.join(slug_parts)}.webp"

def create_gradient_image(width, height, text, output_path):
    """Generates a premium gradient background image with centered Korean text."""
    try:
        # Create gradient array
        image = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(image)
        
        # Harmonious dark/gradient colors
        color_start = (random.randint(5, 15), random.randint(10, 25), random.randint(50, 70))
        color_end = (random.randint(2, 8), random.randint(3, 10), random.randint(20, 30))
        
        for y in range(height):
            r = int(color_start[0] + (color_end[0] - color_start[0]) * (y / height))
            g = int(color_start[1] + (color_end[1] - color_start[1]) * (y / height))
            b = int(color_start[2] + (color_end[2] - color_start[2]) * (y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))
            
        # Try loading a premium font
        font = None
        font_paths = [
            "C:\\Windows\\Fonts\\malgunbd.ttf", # Windows Malgun Gothic Bold
            "C:\\Windows\\Fonts\\malgun.ttf",   # Windows Malgun Gothic
            "/System/Library/Fonts/NanumGothic.ttf", # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" # Linux
        ]
        
        font_size = int(min(width, height) * 0.075)
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    font = ImageFont.truetype(fp, font_size)
                    break
                except:
                    pass
                    
        if font is None:
            # Fallback to default
            font = ImageFont.load_default()
            
        # Draw central decorative rectangle (Sleek card design)
        border_padding = 20
        draw.rectangle(
            [(border_padding, border_padding), (width - border_padding, height - border_padding)],
            outline=(255, 255, 255, 30),
            width=2
        )
        
        # Word wrapping text
        lines = []
        words = text.split()
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            # Rough estimation of width
            if len(test_line) * (font_size * 0.6) > (width - 100):
                if len(current_line) > 1:
                    lines.append(" ".join(current_line[:-1]))
                    current_line = [word]
                else:
                    lines.append(test_line)
                    current_line = []
        if current_line:
            lines.append(" ".join(current_line))
            
        # Draw text centered
        total_text_height = len(lines) * (font_size * 1.3)
        start_y = (height - total_text_height) / 2
        
        for i, line in enumerate(lines):
            # Calculate line width
            line_w = len(line) * (font_size * 0.6) # estimate
            x = (width - line_w) / 2
            y = start_y + i * (font_size * 1.3)
            
            # Simple text shadow for premium depth
            draw.text((x + 2, y + 2), line, fill=(0, 0, 0), font=font)
            draw.text((x, y), line, fill=(255, 255, 255), font=font)
            
        # Save image as webp and optimize
        return save_and_optimize_image(image, output_path, max_size_kb=200)
    except Exception as e:
        sys.stderr.write(f"Image creation error: {str(e)}\n")
        return False

def save_and_optimize_image(img_data, output_path, max_size_kb=200):
    """Saves a PIL Image or raw bytes as optimized WebP under max_size_kb."""
    try:
        if isinstance(img_data, bytes):
            img = Image.open(io.BytesIO(img_data))
        else:
            img = img_data
            
        # Ensure RGB mode
        if img.mode in ('RGBA', 'LA'):
            background = Image.new(img.mode[:-1], img.size, '#ffffff')
            background.paste(img, img.split()[-1])
            img = background
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        quality = 80
        img.save(output_path, "WEBP", quality=quality)
        
        file_size = output_path.stat().st_size
        while file_size > max_size_kb * 1024 and quality > 30:
            quality -= 10
            img.save(output_path, "WEBP", quality=quality)
            file_size = output_path.stat().st_size
            
        # If still larger, scale down
        if file_size > max_size_kb * 1024:
            width, height = img.size
            img = img.resize((int(width * 0.8), int(height * 0.8)), Image.Resampling.LANCZOS)
            img.save(output_path, "WEBP", quality=60)
            
        return True
    except Exception as e:
        sys.stderr.write(f"[ImageGenerator] Save optimization failed: {str(e)}\n")
        return False

def generate_alt_and_caption(keyword, role_desc, api_key=None):
    """Generates alt text and caption using Gemini or falls back to rule-based."""
    api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
    if HAS_GEMINI and api_key.strip():
        try:
            genai.configure(api_key=api_key)
            model = GenerativeModel("gemini-1.5-flash")
            prompt = f"""
블로그 글 키워드: {keyword}
이미지 위치/역할: {role_desc}

위 이미지에 대한 SEO 최적화용 ALT 텍스트(한국어)와 본문에 표시할 자연스러운 이미지 설명 캡션(한국어)을 생성해 주십시오.
반드시 아래 JSON 형식으로만 응답하고, 다른 설명 텍스트나 백틱은 금지합니다.
{{
  "alt": "이미지 상황 및 키워드가 포함된 구체적 ALT 텍스트",
  "caption": "본문 이미지 하단에 노출될 친절하고 자연스러운 설명 캡션 한 문장"
}}
"""
            response = model.generateContent(prompt)
            raw = response.text.strip()
            if raw.startswith("```"):
                raw = re.sub(r'^```json\s*', '', raw, flags=re.IGNORECASE)
                raw = re.sub(r'```$', '', raw).strip()
            parsed = json.loads(raw)
            if "alt" in parsed and "caption" in parsed:
                return parsed["alt"], parsed["caption"]
        except Exception as e:
            sys.stderr.write(f"[ImageGenerator] ALT/Caption Gemini generation failed: {str(e)}\n")
            
    alt = f"{keyword} 관련 {role_desc} 이미지"
    caption = f"▲ {keyword} 관련 {role_desc}를 나타낸 참조 이미지입니다."
    return alt, caption

def generate_imagen_prompt(keyword, api_key=None):
    """Generates Gemini prompt for Imagen 3 in English."""
    api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
    if HAS_GEMINI and api_key.strip():
        try:
            genai.configure(api_key=api_key)
            model = GenerativeModel("gemini-1.5-flash")
            prompt = f"""
핵심 키워드: {keyword}
위 키워드를 다루는 블로그 글의 대표 썸네일/배너 이미지(16:9 비율)를 생성하려고 합니다.
Imagen 3가 고품질 그래픽 이미지를 생성할 수 있도록 영문 이미지 생성 프롬프트를 작성해 주세요.

[규칙]
1. 30단어 내외의 구체적이고 시각적인 묘사로 작성하세요.
2. 텍스트나 글자가 절대 포함되지 않도록 하세요 (e.g. "no text", "no words").
3. 전문적이고 깔끔한 현대적 그래픽/일러스트 스타일로 표현하세요.
4. 오직 영문 프롬프트 텍스트만 출력하세요.
"""
            response = model.generateContent(prompt)
            return response.text.strip()
        except Exception as e:
            sys.stderr.write(f"[ImageGenerator] Prompt translation failed: {str(e)}\n")
            
    return f"A modern professional banner illustration representing {keyword}, digital art style, clean graphics, no text"

def generate_imagen_image(prompt: str, api_key: str = None) -> bytes:
    """Calls Gemini Imagen 3 API via REST to generate an image and returns the bytes."""
    api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
    if not api_key.strip():
        return None
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"
    payload = {
        "instances": [
            {
                "prompt": prompt
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "16:9",
            "outputMimeType": "image/jpeg"
        }
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            predictions = res_data.get("predictions", [])
            if predictions:
                img_b64 = predictions[0].get("bytesBase64Encoded")
                if img_b64:
                    return base64.b64decode(img_b64)
    except Exception as e:
        sys.stderr.write(f"[ImageGenerator] Imagen API 호출 실패: {str(e)}\n")
        
    return None

def embed_images_in_html(keyword, html_content, output_dir_relative):
    """
    Scans the HTML document, extracts keywords/themes from sub-headings,
    generates 3 custom local images, and embeds them at:
    - 20% (After intro / 1st H2)
    - 50% (Middle section)
    - 80% (Before conclusion)
    Optimizes sizes and saves as WebP. Uses Gemini Imagen for Image 1 when possible.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "")
    output_dir = Path(__file__).resolve().parent / ".." / ".." / "web_dashboard" / output_dir_relative
    output_dir.mkdir(parents=True, exist_ok=True)
    
    h2_pattern = re.compile(r'(<h2[^>]*>.*?</h2>)', re.IGNORECASE)
    parts = h2_pattern.split(html_content)
    
    # 1. Representative Banner Image (Image 1) - Try Imagen 3 first
    img_filename_1 = make_seo_filename(keyword, 1)
    img_path_1 = output_dir / img_filename_1
    
    imagen_success = False
    if api_key.strip():
        print("[ImageGenerator] Gemini Imagen 3 API 호출 시도...")
        eng_prompt = generate_imagen_prompt(keyword, api_key)
        print(f"[ImageGenerator] 영문 이미지 프롬프트: {eng_prompt}")
        img_bytes = generate_imagen_image(eng_prompt, api_key)
        if img_bytes:
            imagen_success = save_and_optimize_image(img_bytes, img_path_1, max_size_kb=200)
            if imagen_success:
                print(f"[ImageGenerator] Imagen 3 이미지 생성 및 저장 성공: {img_filename_1}")
                
    if not imagen_success:
        print("[ImageGenerator] Imagen 3 실패 → Pillow 그라디언트 fallback 이미지 생성...")
        create_gradient_image(1200, 630, f"{keyword}\n알아야 할 실전 정보", img_path_1)
        
    # Generate alt and caption for Image 1
    alt_1, cap_1 = generate_alt_and_caption(keyword, "대표 배너 정보", api_key)
    
    # 2. Informational Square Image (Image 2) - Pillow gradient
    img_filename_2 = make_seo_filename(keyword, 2)
    create_gradient_image(800, 800, f"{keyword}\n비교 분석 및 핵심 지표 요약", output_dir / img_filename_2)
    alt_2, cap_2 = generate_alt_and_caption(keyword, "비교 분석 표 요약", api_key)
    
    # 3. Final Summary Image (Image 3) - Pillow gradient
    img_filename_3 = make_seo_filename(keyword, 3)
    create_gradient_image(1200, 630, f"{keyword}\n핵심 요약 및 실행 요령", output_dir / img_filename_3)
    alt_3, cap_3 = generate_alt_and_caption(keyword, "핵심 요약 카드", api_key)
    
    img_filenames = [img_filename_1, img_filename_2, img_filename_3]
    
    # Helper to construct figure HTML tag
    def make_figure_tag(filename, alt, caption):
        return f"""
<figure class="styler-figure" style="margin: 25px 0; text-align: center; font-family: sans-serif;">
  <img src="/{output_dir_relative}/{filename}" alt="{alt}" title="{alt}" style="max-width:100%; height:auto; border-radius:12px; display:block; margin: 0 auto; box-shadow: 0 4px 15px rgba(0,0,0,0.06);" />
  <figcaption style="font-size: 13px; color: #64748b; margin-top: 8px; font-style: italic;">{caption}</figcaption>
</figure>
"""

    if len(parts) < 3:
        # Fallback if H2s are sparse, just append banner
        fig_tag = make_figure_tag(img_filename_1, alt_1, cap_1)
        return html_content + fig_tag, [img_filename_1]
        
    # Reassemble HTML with images injected as figures
    new_html_parts = []
    h2_count = 0
    total_parts = len(parts)
    
    for i, part in enumerate(parts):
        new_html_parts.append(part)
        if h2_pattern.match(part):
            h2_count += 1
            # Inject Image 1 after first H2
            if h2_count == 1:
                fig_tag = make_figure_tag(img_filename_1, alt_1, cap_1)
                new_html_parts.append(fig_tag)
            # Inject Image 2 at roughly 50% H2 count
            elif h2_count == max(2, total_parts // 4):
                fig_tag = make_figure_tag(img_filename_2, alt_2, cap_2)
                new_html_parts.append(fig_tag)
            # Inject Image 3 before final section
            elif i == total_parts - 3:
                fig_tag = make_figure_tag(img_filename_3, alt_3, cap_3)
                new_html_parts.append(fig_tag)
                
    return "".join(new_html_parts), img_filenames

if __name__ == "__main__":
    test_html = """
    <p>안녕하세요. 인트로 부분입니다.</p>
    <h2 id="sec-1">첫 번째 주제</h2>
    <p>본문 내용 1</p>
    <h2 id="sec-2">두 번째 주제</h2>
    <p>본문 내용 2</p>
    <h2 id="sec-3">세 번째 주제</h2>
    <p>결론 내용</p>
    """
    html, files = embed_images_in_html("당뇨 환자 과일", test_html, "output")
    print("Files created:", files)
    print("Final HTML:\n", html)
