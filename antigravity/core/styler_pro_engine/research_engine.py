"""
Research & Data Collection Engine v1.0
뉴스/공식사이트/정부사이트에서 자료를 수집하고 출처를 저장한다.
비용 없이 RSS + 무료 API 기반으로 동작.
"""

import sys
import json
import re
import urllib.request
import urllib.parse
from datetime import datetime
from xml.etree import ElementTree


# ── RSS 피드 파서 ─────────────────────────────────────────────

GOVERNMENT_RSS_FEEDS = {
    "정부24": "https://www.gov.kr/portal/rcvfvrSvc/svcFind/svcSearchRss",
    "고용노동부": "https://www.moel.go.kr/rss/news.do",
    "국세청": "https://www.nts.go.kr/rss/nts_rss.asp",
}

NAVER_NEWS_SEARCH_URL = "https://openapi.naver.com/v1/search/news.json"
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"


def fetch_rss(url, timeout=10):
    """RSS URL에서 뉴스 항목을 파싱한다."""
    items = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            root = ElementTree.fromstring(data)

            # Standard RSS 2.0 or Atom
            for item in root.iter("item"):
                title_el = item.find("title")
                link_el = item.find("link")
                desc_el = item.find("description")
                pub_el = item.find("pubDate")

                items.append({
                    "title": title_el.text.strip() if title_el is not None and title_el.text else "",
                    "url": link_el.text.strip() if link_el is not None and link_el.text else "",
                    "description": _clean_html(desc_el.text.strip()) if desc_el is not None and desc_el.text else "",
                    "published": pub_el.text.strip() if pub_el is not None and pub_el.text else "",
                    "source": "RSS"
                })
    except Exception as e:
        sys.stderr.write(f"[ResearchEngine] RSS 파싱 실패 ({url}): {str(e)}\n")

    return items


def _clean_html(text):
    """HTML 태그를 제거한다."""
    return re.sub(r'<[^>]+>', '', text).strip()


# ── Google News RSS 검색 ──────────────────────────────────────

def search_google_news(keyword, max_results=10):
    """Google News RSS로 키워드 관련 뉴스를 검색한다."""
    encoded = urllib.parse.quote(keyword)
    url = GOOGLE_NEWS_RSS.format(query=encoded)
    items = fetch_rss(url)

    for item in items:
        item["source"] = "Google News"

    return items[:max_results]


# ── 네이버 뉴스 검색 (API 키 필요) ────────────────────────────

def search_naver_news(keyword, max_results=10, client_id="", client_secret=""):
    """네이버 뉴스 검색 API를 호출한다. API 키가 없으면 빈 리스트 반환."""
    import os
    cid = client_id or os.environ.get("NAVER_CLIENT_ID", "")
    csec = client_secret or os.environ.get("NAVER_CLIENT_SECRET", "")

    if not cid or not csec:
        return []

    items = []
    try:
        params = urllib.parse.urlencode({
            "query": keyword, "display": max_results, "sort": "date"
        })
        url = f"{NAVER_NEWS_SEARCH_URL}?{params}"
        req = urllib.request.Request(url, headers={
            "X-Naver-Client-Id": cid,
            "X-Naver-Client-Secret": csec
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            for item in data.get("items", []):
                items.append({
                    "title": _clean_html(item.get("title", "")),
                    "url": item.get("originallink", item.get("link", "")),
                    "description": _clean_html(item.get("description", "")),
                    "published": item.get("pubDate", ""),
                    "source": "Naver News"
                })
    except Exception as e:
        sys.stderr.write(f"[ResearchEngine] 네이버 뉴스 검색 실패: {str(e)}\n")

    return items


# ── 정부 공식 사이트 검색 시뮬레이션 ──────────────────────────

OFFICIAL_SITE_MAP = {
    "정부24": "https://www.gov.kr/search?query={keyword}",
    "복지로": "https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareStIem/wlfareSchSrch.do?searchWrd={keyword}",
    "국세청": "https://www.nts.go.kr/nts/cm/cntnts/cntntsView.do?searchWrd={keyword}",
    "고용노동부": "https://www.moel.go.kr/search/search.do?query={keyword}",
    "건강보험공단": "https://www.nhis.or.kr/nhis/healthIns/retrieveSearchTotal.do?query={keyword}",
    "한국전력": "https://cyber.kepco.co.kr/ckepco/front/jsp/CY/J/A/CYJAPP000.jsp?query={keyword}",
}


def generate_official_links(keyword):
    """키워드 관련 정부/공식 사이트 검색 링크를 생성한다."""
    links = []
    encoded = urllib.parse.quote(keyword)
    for name, url_template in OFFICIAL_SITE_MAP.items():
        links.append({
            "title": f"{name} - {keyword} 검색 결과",
            "url": url_template.format(keyword=encoded),
            "source": name,
            "type": "official"
        })
    return links


# ── 통합 자료 수집 ────────────────────────────────────────────

def collect_research_data(keyword, max_news=10):
    """
    키워드에 대한 자료를 수집하는 통합 함수.
    
    Returns:
        {
            "keyword": str,
            "collected_at": str,
            "news": [...],
            "official_links": [...],
            "total_sources": int,
            "citations": [...]
        }
    """
    news_items = []

    # 1. Google News RSS
    google_news = search_google_news(keyword, max_results=max_news)
    news_items.extend(google_news)

    # 2. 네이버 뉴스 (API 키 있을 때만)
    naver_news = search_naver_news(keyword, max_results=max_news)
    news_items.extend(naver_news)

    # 3. 정부 RSS 피드 (관련성 높은 것만)
    for feed_name, feed_url in GOVERNMENT_RSS_FEEDS.items():
        try:
            rss_items = fetch_rss(feed_url)
            # 키워드 관련 항목만 필터
            relevant = [
                item for item in rss_items
                if keyword in (item.get("title", "") + item.get("description", ""))
            ][:3]
            for item in relevant:
                item["source"] = feed_name
            news_items.extend(relevant)
        except Exception:
            pass

    # 4. 공식 사이트 링크
    official_links = generate_official_links(keyword)

    # 5. 출처 목록 생성 (중복 제거)
    seen_urls = set()
    citations = []
    for item in news_items + official_links:
        url = item.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            citations.append({
                "title": item.get("title", ""),
                "url": url,
                "source": item.get("source", ""),
                "type": item.get("type", "news")
            })

    return {
        "keyword": keyword,
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "news": news_items[:max_news * 2],
        "official_links": official_links,
        "total_sources": len(citations),
        "citations": citations
    }


# ── 출처 블록 생성 (content_builder용) ────────────────────────

def format_citations_block(citations, max_display=5):
    """수집된 출처를 HTML 블록으로 변환한다."""
    if not citations:
        return ""

    items_html = ""
    for cite in citations[:max_display]:
        items_html += f'<li><a href="{cite["url"]}" target="_blank" rel="noopener" style="color: #2563eb; text-decoration: none;">{cite["title"]}</a> <span style="color: #94a3b8; font-size: 0.85em;">({cite["source"]})</span></li>\n'

    return f"""
<div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin: 20px 0;">
  <strong style="display: block; margin-bottom: 8px; color: #334155; font-size: 0.95em;">📋 참고 자료 및 출처</strong>
  <ul style="padding-left: 20px; margin: 0; line-height: 1.8; font-size: 0.88em;">
    {items_html}
  </ul>
</div>
"""


# ── CLI ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Research & Data Collection Engine v1.0")
    parser.add_argument("--keyword", type=str, required=True, help="검색 키워드")
    parser.add_argument("--max-news", type=int, default=10)

    args = parser.parse_args()
    result = collect_research_data(args.keyword, max_news=args.max_news)

    print("---JSON_START---")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("---JSON_END---")
