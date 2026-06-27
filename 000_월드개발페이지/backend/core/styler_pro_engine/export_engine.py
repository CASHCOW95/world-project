import os
import sys
import json
import shutil
from pathlib import Path

def export_assets(keyword, title, blocks, html_content, seo_report, revenue_report, images_list, output_dir_relative="output"):
    """
    Exports output.html, content.json, seo_report.json, and revenue_report.json
    into the web_dashboard/output folder, structuring the images/ directory alongside.
    """
    base_output_dir = Path(__file__).resolve().parent / ".." / ".." / "web_dashboard" / output_dir_relative
    base_output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Save output.html
    html_file = base_output_dir / "output.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # 2. Save content.json
    content_file = base_output_dir / "content.json"
    with open(content_file, "w", encoding="utf-8") as f:
        json.dump({
            "keyword": keyword,
            "title": title,
            "blocks": blocks
        }, f, ensure_ascii=False, indent=2)
        
    # 3. Save seo_report.json
    seo_file = base_output_dir / "seo_report.json"
    with open(seo_file, "w", encoding="utf-8") as f:
        json.dump(seo_report, f, ensure_ascii=False, indent=2)
        
    # 4. Save revenue_report.json
    rev_file = base_output_dir / "revenue_report.json"
    with open(rev_file, "w", encoding="utf-8") as f:
        json.dump(revenue_report, f, ensure_ascii=False, indent=2)
        
    # 5. Build images/ subdirectory and copy/verify WebP images are present
    images_dir = base_output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    exported_images = []
    
    # We will copy the generated WebP images from web_dashboard/output/images to web_dashboard/output/images/
    # Actually, the image_factory already wrote them to web_dashboard/output/images/
    # So we can verify and ensure they are at the correct location, or copy them if generated elsewhere.
    for img in images_list:
        filename = img["filename"]
        # Source image path
        src_path = Path(__file__).resolve().parent / ".." / ".." / "web_dashboard" / "output" / "images" / filename
        dest_path = images_dir / filename
        
        # If src exists, copy to export folder
        if src_path.exists() and src_path != dest_path:
            shutil.copy2(src_path, dest_path)
            
        exported_images.append({
            "filename": filename,
            "alt": img["alt"],
            "title": img["title"],
            "local_path": f"/{output_dir_relative}/images/{filename}"
        })
        
    return {
        "status": "success",
        "output_html": f"/{output_dir_relative}/output.html",
        "content_json": f"/{output_dir_relative}/content.json",
        "seo_report_json": f"/{output_dir_relative}/seo_report.json",
        "revenue_report_json": f"/{output_dir_relative}/revenue_report.json",
        "images": exported_images
    }

if __name__ == "__main__":
    res = export_assets(
        "테스트", "제목", [{"type": "H1", "content": "제목"}],
        "<html></html>", {"score": 90}, {"score": 85},
        [{"filename": "test-guide.webp", "alt": "A", "title": "T"}]
    )
    print(res)
