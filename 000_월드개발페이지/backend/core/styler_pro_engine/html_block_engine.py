import re
import sys
import json

def compile_blocks_to_html(keyword, blocks, ctas, images):
    """
    Assembles content blocks, CTAs, and images into the final unified HTML structure.
    ctas: List of 4 rendered CTA HTML strings.
    images: List of 5 generated image metadata dictionaries.
    """
    
    # Separate Guide (Thumbnail) from body images
    thumbnail_img = None
    body_imgs = []
    
    for img in images:
        if "guide" in img["filename"]:
            thumbnail_img = img
        else:
            body_imgs.append(img)
            
    # Compile Table of Contents (TOC) link list dynamically
    h2_elements = []
    for b in blocks:
        if b["type"] == "H2":
            h2_elements.append({
                "id": b.get("id", f"sec-{len(h2_elements)+1}"),
                "content": b["content"]
            })
            
    # RENDER BLOCKS COMPILING
    compiled_blocks = {}
    
    # 1. H1 (Title)
    h1_block = next((b for b in blocks if b["type"] == "H1"), {"content": f"{keyword} 완벽 정리"})
    compiled_blocks["H1"] = f'<h1 style="font-size: 26px; font-weight: 900; color: #0f172a; text-align: center; margin-bottom: 20px; border-bottom: 2.5px solid #4f46e5; padding-bottom: 12px; font-family: sans-serif;">{h1_block["content"]}</h1>'
    
    # 2. Mock Advertisement Area
    compiled_blocks["AD"] = """
<div class="ad-container" style="background-color: #f8fafc; border: 1.5px dashed #cbd5e1; border-radius: 8px; padding: 15px; margin: 20px 0; text-align: center; font-size: 11px; color: #64748b; font-family: sans-serif;">
  [ ADVERTISEMENT AREA - GOOGLE ADSENSE SPONSOR ]
</div>
    """.strip()
    
    # 3. Table of Contents (TOC)
    toc_li = ""
    for h2 in h2_elements:
        toc_li += f'  <li style="margin-bottom: 8px;"><a href="#{h2["id"]}" style="color: #4f46e5; text-decoration: none; font-weight: bold;">{h2["content"]}</a></li>\n'
        
    compiled_blocks["TOC"] = f"""
<div class="toc-container" style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 20px; margin: 20px 0; font-family: sans-serif;">
  <strong style="font-size: 1.1em; display: block; margin-bottom: 12px; color: #0f172a;">📋 목차 가이드</strong>
  <ul style="list-style-type: none; padding-left: 0; margin-bottom: 0; line-height: 1.8;">
{toc_li}  </ul>
</div>
    """.strip()
    
    # Compilation sequence matching user v2 block layout
    html_out = []
    
    # Append header blocks
    html_out.append(compiled_blocks["H1"])
    
    # Insert Thumbnail if exists
    if thumbnail_img:
        html_out.append(f'<img src="{thumbnail_img["local_path"]}" alt="{thumbnail_img["alt"]}" title="{thumbnail_img["title"]}" style="max-width:100%; height:auto; border-radius:16px; margin-bottom: 25px; display:block; box-shadow: 0 10px 25px rgba(0,0,0,0.08);" />')
        
    html_out.append(compiled_blocks["AD"])
    html_out.append(compiled_blocks["TOC"])
    
    # First CTA below TOC
    if len(ctas) > 0:
        html_out.append(ctas[0])
        
    # Group remaining content blocks by H2 sections
    h2_sections = []
    current_sec = None
    
    for b in blocks:
        if b["type"] == "H2":
            if current_sec:
                h2_sections.append(current_sec)
            current_sec = {"h2": b, "children": []}
        elif b["type"] in ["H3", "PARAGRAPH", "TABLE", "FAQ", "DISCLAIMER", "SUMMARY", "REFERENCES", "CHECKLIST"]:
            if current_sec:
                current_sec["children"].append(b)
            else:
                # Summary or Intro blocks before first H2
                html_out.append(render_single_block(b))
                
    if current_sec:
        h2_sections.append(current_sec)
        
    # Weave H2 sections with images, tables, and CTAs
    table_index = 0
    faq_rendered = False
    
    for idx, sec in enumerate(h2_sections):
        # 1. H2 heading
        h2_node = sec["h2"]
        sec_id = h2_node.get("id", f"sec-{idx+1}")
        html_out.append(f'<h2 id="{sec_id}" style="color: #0f172a; font-size: 21px; font-weight: 800; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-top: 35px; margin-bottom: 15px; font-family: sans-serif;">{h2_node["content"]}</h2>')
        
        # 2. H2 Children
        for child in sec["children"]:
            if child["type"] == "TABLE":
                html_out.append(render_single_block(child))
                table_index += 1
            elif child["type"] == "FAQ":
                html_out.append(render_single_block(child))
                faq_rendered = True
            else:
                html_out.append(render_single_block(child))
                
        # 3. Intersecting Body images (4 slots)
        if idx < len(body_imgs):
            img = body_imgs[idx]
            html_out.append(f'<img src="{img["local_path"]}" alt="{img["alt"]}" title="{img["title"]}" style="max-width:100%; height:auto; border-radius:12px; margin:25px 0; display:block; box-shadow: 0 4px 15px rgba(0,0,0,0.06);" />')
            
        # 4. Intersecting CTAs at designated spots
        if idx == 1 and len(ctas) > 1:
            html_out.append(ctas[1])
        elif idx == 3 and len(ctas) > 2:
            html_out.append(ctas[2])
            
    # Append final CTA if not yet appended
    if len(ctas) > 3:
        html_out.append(ctas[3])
        
    # Append Disclaimer if not appended
    disclaimer_block = next((b for b in blocks if b["type"] == "DISCLAIMER"), None)
    if disclaimer_block:
        html_out.append(render_single_block(disclaimer_block))
        
    # Wrap entire post inside a white card wrapper to secure legible dark-text formatting across both dark/light browser preferences.
    wrapped_html = f"""
<div class="styler-content-wrapper" style="background-color: #ffffff; color: #1e293b; padding: 25px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); font-family: sans-serif; line-height: 1.8; text-align: left; max-width: 100%; box-sizing: border-box; overflow-x: hidden;">
<style>
  .styler-content-wrapper {{
    color: #1e293b !important;
  }}
  .styler-content-wrapper h1, .styler-content-wrapper h2 {{
    color: #0f172a !important;
  }}
  .styler-content-wrapper h3 {{
    color: #1e293b !important;
  }}
  .styler-content-wrapper p {{
    color: #334155 !important;
  }}
  .styler-content-wrapper li a {{
    color: #4f46e5 !important;
  }}
  .styler-content-wrapper th {{
    color: #0f172a !important;
    background-color: #f1f5f9 !important;
  }}
  .styler-content-wrapper td {{
    color: #334155 !important;
  }}
  .styler-content-wrapper .faq-item strong {{
    color: #1e293b !important;
  }}
  .styler-content-wrapper .faq-item span {{
    color: #475569 !important;
  }}
  .styler-content-wrapper .disclaimer-container {{
    color: #475569 !important;
  }}
  .styler-content-wrapper a[style*="linear-gradient"], 
  .styler-content-wrapper a[style*="background"] {{
    color: #ffffff !important;
  }}
  .styler-content-wrapper .cta-block-banner span {{
    color: #1e293b !important;
  }}
  .styler-content-wrapper .cta-block-card p {{
    color: #475569 !important;
  }}
</style>
{"\n".join(html_out)}
</div>
    """.strip()
    return wrapped_html

def render_single_block(b):
    t = b["type"]
    
    if t == "SUMMARY":
        return f'<p style="font-size: 14.5px; line-height: 1.8; color: #475569; font-weight: 500; margin-bottom: 20px; font-family: sans-serif;">{b["content"]}</p>'
        
    elif t == "H3":
        return f'<h3 style="color: #1e293b; font-size: 16.5px; font-weight: 700; margin-top: 25px; margin-bottom: 10px; font-family: sans-serif;">{b["content"]}</h3>'
        
    elif t == "PARAGRAPH":
        return f'<p style="font-size: 13.5px; line-height: 1.75; color: #334155; margin-bottom: 15px; font-family: sans-serif;">{b["content"]}</p>'
        
    elif t == "TABLE":
        headers_html = "".join([f'<th style="border: 1px solid #e2e8f0; padding: 10px; background: #f1f5f9; color: #0f172a; font-weight: bold;">{h}</th>' for h in b["headers"]])
        
        rows_html = ""
        for r_idx, row in enumerate(b["rows"]):
            bg_color = "#f8fafc" if r_idx % 2 == 1 else "#ffffff"
            cells = "".join([f'<td style="border: 1px solid #e2e8f0; padding: 10px; color: #334155;">{c}</td>' for c in row])
            rows_html += f'  <tr style="border-bottom: 1px solid #e2e8f0; background-color: {bg_color};">{cells}</tr>\n'
            
        return f"""
<table class="styler-table" style="width:100%; border-collapse:collapse; text-align:center; margin:20px 0; font-size:12.5px; border: 1px solid #e2e8f0; font-family: sans-serif;">
  <thead>
    <tr>{headers_html}</tr>
  </thead>
  <tbody>
{rows_html}  </tbody>
</table>
        """.strip()
        
    elif t == "FAQ":
        faq_li = ""
        for item in b["items"]:
            faq_li += f"""
  <div class="faq-item" style="border-bottom: 1px solid #e2e8f0; padding: 15px 0;">
    <strong style="color: #1e293b; display: block; margin-bottom: 6px; font-size: 13.5px; font-family: sans-serif;">{item["question"]}</strong>
    <span style="color: #475569; display: block; line-height: 1.7; font-size: 13px; font-family: sans-serif;">{item["answer"]}</span>
  </div>
            """.strip()
            
        return f"""
<div class="faq-container" style="background: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 16px; padding: 20px; margin: 25px 0; font-family: sans-serif;">
  <strong style="font-size: 15px; color: #0f172a; display: block; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 10px; margin-bottom: 10px;">❓ 자주 묻는 FAQ 답변 {len(b["items"])}선</strong>
  {faq_li}
</div>
        """.strip()

    elif t == "DISCLAIMER":
        return f"""
<div class="disclaimer-container" style="background-color: #f8fafc; border-left: 4px solid #94a3b8; padding: 15px; border-radius: 6px; font-size: 11px; color: #475569; margin: 30px 0; line-height: 1.7; font-family: sans-serif;">
  {b["content"]}
</div>
        """.strip()
        
    elif t == "REFERENCES":
        items_html = ""
        for cite in b.get("items", []):
            title = cite.get("title", "")
            url = cite.get("url", "")
            source = cite.get("source", "")
            items_html += f'<li style="margin-bottom: 6px;"><a href="{url}" target="_blank" rel="noopener" style="color: #4f46e5; text-decoration: none; font-weight: 600;">{title}</a> <span style="color: #64748b; font-size: 0.85em;">({source})</span></li>\n'
        return f"""
<div class="references-container" style="background-color: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 18px; margin: 25px 0; font-family: sans-serif;">
  <strong style="display: block; margin-bottom: 10px; color: #0f172a; font-size: 14px;">📋 참고 자료 및 공식 출처</strong>
  <ul style="padding-left: 20px; margin: 0; line-height: 1.7; font-size: 12.5px;">
    {items_html}
  </ul>
</div>
        """.strip()
        
    elif t == "CHECKLIST":
        items_html = ""
        for item in b.get("items", []):
            items_html += f'<li style="margin-bottom: 8px; display: flex; align-items: flex-start; font-size: 13px;"><span style="color: #10b981; font-weight: bold; margin-right: 8px;">✓</span> <span style="color: #334155;">{item}</span></li>\n'
        return f"""
<div class="checklist-container" style="background-color: #f0fdf4; border: 1.5px solid #bbf7d0; border-radius: 12px; padding: 18px; margin: 25px 0; font-family: sans-serif;">
  <strong style="display: block; margin-bottom: 12px; color: #14532d; font-size: 14px;">✅ 핵심 체크리스트 / 자가 진단</strong>
  <ul style="list-style-type: none; padding-left: 0; margin: 0;">
    {items_html}
  </ul>
</div>
        """.strip()
        
    return ""

if __name__ == "__main__":
    test_blocks = [
        {"type": "H1", "content": "제목"},
        {"type": "SUMMARY", "content": "요약"},
        {"type": "H2", "id": "sec-1", "content": "대주제 1"},
        {"type": "PARAGRAPH", "content": "본문문단"},
        {"type": "TABLE", "headers": ["A", "B"], "rows": [["1", "2"]]},
        {"type": "FAQ", "items": [{"question": "Q", "answer": "A"}]}
    ]
    html = compile_blocks_to_html("감기", test_blocks, ["CTA1", "CTA2"], [{"filename": "guide.webp", "local_path": "guide.webp", "alt": "A", "title": "T"}])
    print(html)
