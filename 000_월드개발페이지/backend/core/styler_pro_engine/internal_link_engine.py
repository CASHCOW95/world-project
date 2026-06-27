"""
Internal Link Graph Engine v1.0 (핵심 엔진)
발행 후 URL 저장 → 클러스터 내/외부 링크 매핑 → 본문 수정 → 재발행.
"""

import sys
import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "styler_pro_x_v2.db"


# ── DB 스키마 초기화 ──────────────────────────────────────────

def init_link_tables(db_path=None):
    """내부링크 관련 테이블을 생성한다 (없으면)."""
    conn = sqlite3.connect(str(db_path or DB_PATH))
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS clusters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_keyword TEXT NOT NULL,
            sub_count INTEGER DEFAULT 0,
            cluster_json TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS published_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cluster_id INTEGER,
            role TEXT DEFAULT 'main',
            keyword TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT,
            platform TEXT DEFAULT 'tistory',
            html_hash TEXT,
            status TEXT DEFAULT 'pending',
            published_at TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (cluster_id) REFERENCES clusters(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS internal_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_post_id INTEGER NOT NULL,
            target_post_id INTEGER NOT NULL,
            anchor_text TEXT NOT NULL,
            link_type TEXT DEFAULT 'cluster',
            inserted_at TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (source_post_id) REFERENCES published_posts(id),
            FOREIGN KEY (target_post_id) REFERENCES published_posts(id)
        )
    """)

    conn.commit()
    conn.close()


# ── 클러스터 저장 ─────────────────────────────────────────────

def save_cluster(main_keyword, cluster_json, db_path=None):
    """클러스터 구조를 DB에 저장하고 cluster_id를 반환."""
    init_link_tables(db_path)
    conn = sqlite3.connect(str(db_path or DB_PATH))
    c = conn.cursor()

    sub_count = len(cluster_json.get("subs", []))
    c.execute(
        "INSERT INTO clusters (main_keyword, sub_count, cluster_json, status) VALUES (?, ?, ?, ?)",
        (main_keyword, sub_count, json.dumps(cluster_json, ensure_ascii=False), "pending")
    )
    cluster_id = c.lastrowid
    conn.commit()
    conn.close()
    return cluster_id


# ── 발행 URL 저장 ────────────────────────────────────────────

def save_published_post(cluster_id, role, keyword, title, url, platform="tistory", html_hash="", db_path=None):
    """발행된 글의 URL과 메타 정보를 저장한다."""
    init_link_tables(db_path)
    conn = sqlite3.connect(str(db_path or DB_PATH))
    c = conn.cursor()

    c.execute(
        """INSERT INTO published_posts 
           (cluster_id, role, keyword, title, url, platform, html_hash, status, published_at) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (cluster_id, role, keyword, title, url, platform, html_hash,
         "published", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    post_id = c.lastrowid
    conn.commit()
    conn.close()
    return post_id


# ── 링크 매핑 생성 ────────────────────────────────────────────

def build_link_map(cluster_id, db_path=None):
    """
    클러스터 내 모든 발행된 글을 조회하여 링크 매핑을 생성한다.
    
    Returns:
        {
            "main": { "post_id": int, "title": str, "url": str },
            "subs": [ { "post_id": int, "title": str, "url": str, "anchor": str } ],
            "links": [
                { "source_id": int, "target_id": int, "anchor": str, "direction": str }
            ]
        }
    """
    init_link_tables(db_path)
    conn = sqlite3.connect(str(db_path or DB_PATH))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 클러스터의 원본 구조 로드
    c.execute("SELECT cluster_json FROM clusters WHERE id = ?", (cluster_id,))
    row = c.fetchone()
    cluster_json = json.loads(row["cluster_json"]) if row else {}

    # 발행된 글 목록
    c.execute(
        "SELECT id, role, keyword, title, url FROM published_posts WHERE cluster_id = ? AND status = 'published' ORDER BY id",
        (cluster_id,)
    )
    posts = [dict(r) for r in c.fetchall()]
    conn.close()

    if not posts:
        return {"main": None, "subs": [], "links": []}

    main_post = None
    sub_posts = []
    for p in posts:
        if p["role"] == "main":
            main_post = p
        else:
            sub_posts.append(p)

    # 앵커 텍스트 매핑 (클러스터 JSON에서 가져오기)
    sub_anchors = {}
    for sub_def in cluster_json.get("subs", []):
        sub_anchors[sub_def.get("title", "")] = sub_def.get("anchor", "관련 글 보기")

    # 링크 생성: 메인 → 각 서브, 각 서브 → 메인
    links = []

    if main_post:
        for sp in sub_posts:
            anchor = sub_anchors.get(sp["title"], f"{sp['keyword']} 상세보기")
            # 메인 → 서브
            links.append({
                "source_id": main_post["id"],
                "target_id": sp["id"],
                "anchor": anchor,
                "direction": "main_to_sub"
            })
            # 서브 → 메인
            links.append({
                "source_id": sp["id"],
                "target_id": main_post["id"],
                "anchor": f"{main_post['keyword']} 종합 가이드 보기",
                "direction": "sub_to_main"
            })

        # 서브 ↔ 서브 (인접한 서브글 간 연결, 최대 2개)
        for i, sp in enumerate(sub_posts):
            neighbors = []
            if i > 0:
                neighbors.append(sub_posts[i - 1])
            if i < len(sub_posts) - 1:
                neighbors.append(sub_posts[i + 1])
            for nb in neighbors:
                links.append({
                    "source_id": sp["id"],
                    "target_id": nb["id"],
                    "anchor": f"{nb['keyword']} 함께 읽기",
                    "direction": "sub_to_sub"
                })

    # 서브 포스트에 앵커 추가
    for sp in sub_posts:
        sp["anchor"] = sub_anchors.get(sp["title"], "관련 글 보기")

    return {
        "main": main_post,
        "subs": sub_posts,
        "links": links
    }


# ── 본문에 내부링크 버튼 삽입 ─────────────────────────────────

def _make_link_button_html(url, anchor_text):
    """CTA 버튼 스타일의 내부링크 HTML을 생성."""
    return f"""
<div style="margin: 18px 0; text-align: center;">
  <a href="{url}" 
     style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; padding: 12px 28px; border-radius: 50px; text-decoration: none; 
            font-weight: bold; font-size: 14px; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3); 
            transition: 0.2s;"
     onmouseover="this.style.transform='translateY(-2px)'" 
     onmouseout="this.style.transform='translateY(0)'">
    👉 {anchor_text}
  </a>
</div>
"""


def _make_related_links_box(links_data):
    """관련 글 목록을 박스 형태로 생성."""
    items_html = ""
    for ld in links_data[:3]:  # 최대 3개
        items_html += f'<li style="margin: 6px 0;"><a href="{ld["url"]}" style="color: #1d4ed8; text-decoration: none; font-weight: 600;">📌 {ld["anchor"]}</a></li>\n'

    return f"""
<div style="background-color: #f8fafc; border: 1.5px solid #cbd5e1; border-radius: 12px; padding: 18px; margin: 20px 0;">
  <strong style="display: block; margin-bottom: 8px; color: #334155;">📚 함께 읽으면 좋은 글</strong>
  <ul style="list-style: none; padding: 0; margin: 0;">
    {items_html}
  </ul>
</div>
"""


def inject_internal_links(html_content, post_id, link_map):
    """
    HTML 본문에 내부링크를 삽입한다.
    
    - 메인글: FAQ 위에 서브글 버튼 목록 삽입
    - 서브글: 결론 위에 메인글 링크 + 관련 서브글 박스 삽입
    """
    is_main = link_map["main"] and link_map["main"]["id"] == post_id

    if is_main:
        # 메인글 → 서브글 버튼들 삽입
        buttons_html = "\n".join([
            _make_link_button_html(sp["url"], sp["anchor"])
            for sp in link_map["subs"]
            if sp.get("url")
        ])

        if buttons_html:
            # FAQ 앞에 삽입 시도
            faq_pattern = re.compile(r'(<div[^>]*class="faq|<h2[^>]*>.*?FAQ|<h2[^>]*>.*?자주\s*묻는)', re.IGNORECASE)
            match = faq_pattern.search(html_content)
            if match:
                insert_pos = match.start()
                html_content = html_content[:insert_pos] + buttons_html + "\n" + html_content[insert_pos:]
            else:
                # FAQ 못 찾으면 마지막 H2 앞에 삽입
                last_h2 = list(re.finditer(r'<h2', html_content, re.IGNORECASE))
                if last_h2:
                    insert_pos = last_h2[-1].start()
                    html_content = html_content[:insert_pos] + buttons_html + "\n" + html_content[insert_pos:]
                else:
                    html_content += buttons_html
    else:
        # 서브글 → 메인글 버튼 + 관련 서브글 박스
        inject_parts = []

        # 메인글 링크
        if link_map["main"] and link_map["main"].get("url"):
            inject_parts.append(
                _make_link_button_html(link_map["main"]["url"], f"{link_map['main']['keyword']} 종합 가이드 보기")
            )

        # 관련 서브글 (자기 자신 제외, 최대 2개)
        related_subs = [
            {"url": sp["url"], "anchor": sp["anchor"]}
            for sp in link_map["subs"]
            if sp["id"] != post_id and sp.get("url")
        ][:2]

        if related_subs:
            inject_parts.append(_make_related_links_box(related_subs))

        if inject_parts:
            inject_html = "\n".join(inject_parts)
            # 면책조항 앞에 삽입 시도
            disclaimer_pattern = re.compile(r'(<div[^>]*면책|<div[^>]*disclaimer|💡\s*면책)', re.IGNORECASE)
            match = disclaimer_pattern.search(html_content)
            if match:
                insert_pos = match.start()
                html_content = html_content[:insert_pos] + inject_html + "\n" + html_content[insert_pos:]
            else:
                html_content += inject_html

    return html_content


# ── 링크 기록 저장 ────────────────────────────────────────────

def save_link_records(link_map, db_path=None):
    """생성된 링크 매핑을 DB에 저장한다."""
    init_link_tables(db_path)
    conn = sqlite3.connect(str(db_path or DB_PATH))
    c = conn.cursor()

    for lk in link_map.get("links", []):
        c.execute(
            "INSERT INTO internal_links (source_post_id, target_post_id, anchor_text, link_type) VALUES (?, ?, ?, ?)",
            (lk["source_id"], lk["target_id"], lk["anchor"], lk["direction"])
        )

    conn.commit()
    conn.close()


# ── 발행 이력 조회 ────────────────────────────────────────────

def get_published_posts(limit=50, db_path=None):
    """최근 발행된 글 목록을 조회한다."""
    init_link_tables(db_path)
    conn = sqlite3.connect(str(db_path or DB_PATH))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(
        "SELECT * FROM published_posts ORDER BY published_at DESC LIMIT ?",
        (limit,)
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_link_graph(db_path=None):
    """전체 내부링크 그래프를 조회한다."""
    init_link_tables(db_path)
    conn = sqlite3.connect(str(db_path or DB_PATH))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
        SELECT il.*, 
               sp.title as source_title, sp.url as source_url,
               tp.title as target_title, tp.url as target_url
        FROM internal_links il
        JOIN published_posts sp ON il.source_post_id = sp.id
        JOIN published_posts tp ON il.target_post_id = tp.id
        ORDER BY il.inserted_at DESC
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_dashboard_stats(db_path=None):
    """운영 대시보드용 통계를 조회한다."""
    init_link_tables(db_path)
    conn = sqlite3.connect(str(db_path or DB_PATH))
    c = conn.cursor()

    stats = {}
    c.execute("SELECT COUNT(*) FROM published_posts WHERE status = 'published'")
    stats["total_published"] = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM published_posts WHERE status = 'pending'")
    stats["total_pending"] = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM published_posts WHERE status = 'failed'")
    stats["total_failed"] = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM clusters")
    stats["total_clusters"] = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM internal_links")
    stats["total_links"] = c.fetchone()[0]

    # 오늘 발행 수
    c.execute("SELECT COUNT(*) FROM published_posts WHERE date(published_at) = date('now', 'localtime') AND status = 'published'")
    stats["today_published"] = c.fetchone()[0]

    conn.close()
    return stats


# ── CLI 테스트 ─────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Internal Link Graph Engine v1.0")
    parser.add_argument("--test", action="store_true", help="테스트 실행")
    parser.add_argument("--stats", action="store_true", help="대시보드 통계 조회")
    parser.add_argument("--posts", action="store_true", help="발행 완료 목록 조회")
    parser.add_argument("--graph", action="store_true", help="내부링크 그래프 조회")
    args = parser.parse_args()

    if args.stats:
        print(json.dumps(get_dashboard_stats(), ensure_ascii=False, indent=2))
    elif args.posts:
        print(json.dumps(get_published_posts(), ensure_ascii=False, indent=2))
    elif args.graph:
        print(json.dumps(get_link_graph(), ensure_ascii=False, indent=2))
    elif args.test:
        init_link_tables()
        print("[OK] 내부링크 테이블 초기화 완료")
        print("[OK] 대시보드 통계:", json.dumps(get_dashboard_stats(), ensure_ascii=False))
    else:
        parser.print_help()
