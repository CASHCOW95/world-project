import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "styler_pro_x_v2.db"

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # 1. keywords table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
            keyword TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            search_volume INTEGER NOT NULL,
            competition INTEGER NOT NULL,
            cpc TEXT NOT NULL,
            golden_score INTEGER NOT NULL
        )
    """)
    
    # 2. contents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            title TEXT NOT NULL,
            raw_text TEXT NOT NULL, -- Holds JSON blocks structure
            assembled_html TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # 3. images table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            alt TEXT NOT NULL,
            title TEXT NOT NULL,
            local_path TEXT NOT NULL,
            FOREIGN KEY(content_id) REFERENCES contents(id)
        )
    """)
    
    # 4. seo_reports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seo_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            final_score INTEGER NOT NULL,
            readability INTEGER NOT NULL,
            length_score INTEGER NOT NULL,
            checklist_json TEXT NOT NULL,
            FOREIGN KEY(content_id) REFERENCES contents(id)
        )
    """)
    
    # 5. revenue_reports table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS revenue_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            profit_score INTEGER NOT NULL,
            expected_cpc TEXT NOT NULL,
            breakdown_json TEXT NOT NULL,
            FOREIGN KEY(content_id) REFERENCES contents(id)
        )
    """)
    
    conn.commit()
    conn.close()

def save_generation_data(keyword_info, title, blocks_json, assembled_html, images_list, seo_score, seo_details, profit_score, profit_details):
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # 1. Save or Update Keyword
    cursor.execute("""
        INSERT OR REPLACE INTO keywords (keyword, category, search_volume, competition, cpc, golden_score)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        keyword_info["keyword"],
        keyword_info.get("category", "lifestyle"),
        keyword_info["search_volume"],
        keyword_info["competition"],
        keyword_info["cpc"],
        keyword_info["golden_score"]
    ))
    
    # 2. Save Content
    created_at = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO contents (keyword, title, raw_text, assembled_html, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (keyword_info["keyword"], title, blocks_json, assembled_html, created_at))
    content_id = cursor.lastrowid
    
    # 3. Save Images
    for img in images_list:
        cursor.execute("""
            INSERT INTO images (content_id, filename, alt, title, local_path)
            VALUES (?, ?, ?, ?, ?)
        """, (content_id, img["filename"], img["alt"], img["title"], img["local_path"]))
        
    # 4. Save SEO Report
    cursor.execute("""
        INSERT INTO seo_reports (content_id, final_score, readability, length_score, checklist_json)
        VALUES (?, ?, ?, ?, ?)
    """, (
        content_id,
        seo_score,
        seo_details.get("readability", {}).get("score", 0),
        seo_details.get("length", {}).get("score", 0),
        json.dumps(seo_details)
    ))
    
    # 5. Save Revenue Report
    cursor.execute("""
        INSERT INTO revenue_reports (content_id, profit_score, expected_cpc, breakdown_json)
        VALUES (?, ?, ?, ?)
    """, (
        content_id,
        profit_score,
        profit_details.get("cpc_rating", "보통"),
        json.dumps(profit_details)
    ))
    
    conn.commit()
    conn.close()
    return content_id

def get_history():
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Fetch content details joined with scores
    cursor.execute("""
        SELECT 
            c.id, c.keyword, c.title, c.assembled_html, c.created_at,
            s.final_score, r.profit_score, r.expected_cpc, r.breakdown_json
        FROM contents c
        LEFT JOIN seo_reports s ON c.id = s.content_id
        LEFT JOIN revenue_reports r ON c.id = r.content_id
        ORDER BY c.id DESC
    """)
    rows = cursor.fetchall()
    
    history = []
    for r in rows:
        content_id = r[0]
        # Fetch associated images
        cursor.execute("SELECT filename, alt, title, local_path FROM images WHERE content_id = ?", (content_id,))
        img_rows = cursor.fetchall()
        images = [{"filename": im[0], "alt": im[1], "title": im[2], "local_path": im[3]} for im in img_rows]
        
        # Parse breakdown details for advanced profit panel and image prompts restoration
        profit_details = {}
        if r[8]:
            try:
                profit_details = json.loads(r[8])
            except Exception:
                pass
        
        history.append({
            "id": content_id,
            "keyword": r[1],
            "title": r[2],
            "html_content": r[3],
            "created_at": r[4],
            "seo_score": r[5] or 0,
            "profit_score": r[6] or 0,
            "expected_cpc": r[7] or "보통",
            "images": images,
            "cpc_dollar": profit_details.get("cpc_dollar"),
            "estimated_visitors": profit_details.get("estimated_visitors"),
            "ctr": profit_details.get("ctr"),
            "estimated_revenue": profit_details.get("estimated_revenue"),
            "affiliate_product": profit_details.get("affiliate_product"),
            "ai_badge": profit_details.get("ai_badge"),
            "blue_ocean_score": profit_details.get("blue_ocean_score"),
            "blue_ocean_recommend": profit_details.get("blue_ocean_recommend"),
            "image_prompts": profit_details.get("image_prompts")
        })
        
    conn.close()
    return history


if __name__ == "__main__":
    import sys
    init_db()
    if "--history" in sys.argv:
        print(json.dumps(get_history(), ensure_ascii=False))
    else:
        print("Styler Pro X v2 Database initialized at:", DB_PATH)
