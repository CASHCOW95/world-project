import os
import sys
import random
import re
from pathlib import Path

# Ensure PIL is imported or auto-installed
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        from PIL import Image, ImageDraw, ImageFont
    except Exception as e:
        sys.stderr.write(f"Failed to load Pillow: {str(e)}\n")

# English translating helper for slug filenames
TRANSLATION_MAP = {
    "여권": "passport",
    "발급": "issue",
    "절차": "procedure",
    "미성년자": "minor",
    "수수료": "fee",
    "정부지원금": "subsidy",
    "조회": "search",
    "감기몸살": "cold-flu",
    "빨리": "fast",
    "낫는": "cure",
    "법": "method",
    "전기세": "electricity",
    "절약": "save",
    "방법": "how-to",
    "노트북": "laptop",
    "가성비": "budget",
    "추천": "recommendation",
    "대출": "loan",
    "금리": "interest-rate"
}

def make_seo_slug(keyword):
    # Strip special chars and check mapping
    normalized = keyword.lower()
    slug_parts = []
    
    for kr, en in TRANSLATION_MAP.items():
        if kr in normalized:
            slug_parts.append(en)
            
    if not slug_parts:
        # Fallback regex clean
        clean = re.sub(r'[^a-zA-Z0-9]', '-', keyword)
        clean = re.sub(r'-+', '-', clean).strip('-').lower()
        return clean if clean else "blog-post"
        
    return "-".join(slug_parts)

def create_factory_image(width, height, text, output_path):
    """Draws a high-quality visual text card with gradient backgrounds."""
    try:
        image = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(image)
        
        # Premium deep-colored gradients
        r1, g1, b1 = random.randint(10, 35), random.randint(15, 30), random.randint(70, 100)
        r2, g2, b2 = random.randint(5, 12), random.randint(5, 12), random.randint(20, 35)
        
        for y in range(height):
            r = int(r1 + (r2 - r1) * (y / height))
            g = int(g1 + (g2 - g1) * (y / height))
            b = int(b1 + (b2 - b1) * (y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))
            
        # UI card bounds
        pad = int(min(width, height) * 0.04)
        draw.rectangle([(pad, pad), (width - pad, height - pad)], outline=(255, 255, 255, 25), width=2)
        
        # Load font
        font = None
        font_paths = [
            "C:\\Windows\\Fonts\\malgunbd.ttf",
            "C:\\Windows\\Fonts\\malgun.ttf",
            "/System/Library/Fonts/NanumGothic.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]
        font_size = int(min(width, height) * 0.065)
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    font = ImageFont.truetype(fp, font_size)
                    break
                except:
                    pass
        if not font:
            font = ImageFont.load_default()
            
        # Draw text
        lines = text.split("\n")
        total_h = len(lines) * (font_size * 1.3)
        start_y = (height - total_h) / 2
        
        for i, line in enumerate(lines):
            line_w = len(line) * (font_size * 0.65) # Estimate width
            x = (width - line_w) / 2
            y = start_y + i * (font_size * 1.3)
            
            # Shadow
            draw.text((x + 2, y + 2), line, fill=(0, 0, 0), font=font)
            draw.text((x, y), line, fill=(255, 255, 255), font=font)
            
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, "WEBP", quality=90)
        return True
    except Exception as e:
        sys.stderr.write(f"PIL draw error: {str(e)}\n")
        return False

def make_5_images(keyword, output_dir_relative="output/images"):
    slug = make_seo_slug(keyword)
    output_dir = Path(__file__).resolve().parent / ".." / ".." / "web_dashboard" / output_dir_relative
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 5 targets
    # 1. Representative (1200x630) - keyword-guide.webp
    # 2. Comparison table (1000x1000) - keyword-table.webp
    # 3. Summary card (1000x1000) - keyword-summary.webp
    # 4. Body Infographic (1000x1000) - keyword-infographic.webp
    # 5. Core values card (1000x1000) - keyword-body.webp
    
    targets = [
        {"file": f"{slug}-guide.webp", "width": 1200, "height": 630, "text": f"{keyword}\n공식 안내 가이드", "alt": f"{keyword} 절차 설명 이미지", "title": f"{keyword} 가이드"},
        {"file": f"{slug}-table.webp", "width": 1000, "height": 1000, "text": f"{keyword}\n비교 분석 지표 및 데이터", "alt": f"{keyword} 비교표 상세 분석 이미지", "title": f"{keyword} 비교표"},
        {"file": f"{slug}-summary.webp", "width": 1000, "height": 1000, "text": f"{keyword}\n핵심 요점 3줄 요약 카드", "alt": f"{keyword} 핵심 요점 카드 이미지", "title": f"{keyword} 요약 카드"},
        {"file": f"{slug}-infographic.webp", "width": 1000, "height": 1000, "text": f"{keyword}\n단계별 프로세스 인포그래픽", "alt": f"{keyword} 실전 절차 인포그래픽 이미지", "title": f"{keyword} 인포그래픽"},
        {"file": f"{slug}-body.webp", "width": 1000, "height": 1000, "text": f"{keyword}\n놓치기 쉬운 부작용 및 주의사항", "alt": f"{keyword} 주의사항 정보 이미지", "title": f"{keyword} 주의사항"}
    ]
    
    image_metadata_list = []
    for t in targets:
        file_path = output_dir / t["file"]
        create_factory_image(t["width"], t["height"], t["text"], file_path)
        
        # Web-accessible URL path
        web_path = f"/{output_dir_relative}/{t["file"]}"
        image_metadata_list.append({
            "filename": t["file"],
            "alt": t["alt"],
            "title": t["title"],
            "local_path": web_path,
            "dimensions": f"{t['width']}x{t['height']}"
        })
        
    return image_metadata_list

if __name__ == "__main__":
    res = make_5_images("미성년자 여권발급 절차")
    print(res)
