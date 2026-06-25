"""
Telegram Notification Bot v1.0
발행 알림, 에러 알림, 일일 리포트를 텔레그램으로 전송한다.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime


TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/{method}"


def _get_config():
    """환경 변수에서 텔레그램 봇 설정을 가져온다."""
    return {
        "token": os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        "chat_id": os.environ.get("TELEGRAM_CHAT_ID", ""),
    }


def _call_telegram_api(token, method, params):
    """텔레그램 Bot API를 호출한다."""
    url = TELEGRAM_API_BASE.format(token=token, method=method)
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        sys.stderr.write(f"[TelegramBot] API 호출 실패: {str(e)}\n")
        return None


def send_message(text, parse_mode="HTML", token=None, chat_id=None):
    """텔레그램 메시지를 전송한다."""
    config = _get_config()
    tk = token or config["token"]
    cid = chat_id or config["chat_id"]

    if not tk or not cid:
        sys.stderr.write("[TelegramBot] 토큰 또는 chat_id 미설정. 알림 스킵.\n")
        return False

    result = _call_telegram_api(tk, "sendMessage", {
        "chat_id": cid,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": "true"
    })

    return result and result.get("ok", False)


# ── 발행 완료 알림 ────────────────────────────────────────────

def notify_publish_success(title, url, keyword, platform="tistory"):
    """글 발행 성공 알림을 전송한다."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"""✅ <b>발행 완료</b>

📝 <b>{title}</b>
🔑 키워드: {keyword}
📡 플랫폼: {platform}
🔗 <a href="{url}">게시글 링크</a>
⏰ {now}"""

    return send_message(msg)


# ── 에러 알림 ─────────────────────────────────────────────────

def notify_error(stage, keyword, error_msg):
    """파이프라인 에러 알림을 전송한다."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"""⚠️ <b>에러 발생</b>

🔴 단계: {stage}
🔑 키워드: {keyword}
💥 에러: <code>{error_msg[:300]}</code>
⏰ {now}"""

    return send_message(msg)


# ── 클러스터 발행 시작 알림 ────────────────────────────────────

def notify_cluster_start(main_keyword, sub_count):
    """클러스터 발행 시작 알림."""
    msg = f"""🚀 <b>클러스터 발행 시작</b>

🎯 메인 키워드: {main_keyword}
📄 서브글 수: {sub_count}개
⏰ {datetime.now().strftime("%Y-%m-%d %H:%M")}"""

    return send_message(msg)


# ── 클러스터 발행 완료 알림 ────────────────────────────────────

def notify_cluster_complete(main_keyword, total, success, failed):
    """클러스터 전체 발행 완료 알림."""
    status_icon = "✅" if failed == 0 else "⚠️"
    msg = f"""{status_icon} <b>클러스터 발행 완료</b>

🎯 메인 키워드: {main_keyword}
📊 결과: 총 {total}건 중 성공 {success}건 / 실패 {failed}건
⏰ {datetime.now().strftime("%Y-%m-%d %H:%M")}"""

    return send_message(msg)


# ── 일일 리포트 ───────────────────────────────────────────────

def send_daily_report(stats):
    """
    일일 운영 리포트를 전송한다.
    stats: internal_link_engine.get_dashboard_stats()의 반환값
    """
    now = datetime.now().strftime("%Y년 %m월 %d일")
    msg = f"""📊 <b>일일 블로그 운영 리포트</b>
━━━━━━━━━━━━━━━━
📅 {now}

📌 <b>오늘 발행</b>: {stats.get('today_published', 0)}건
📄 <b>총 발행</b>: {stats.get('total_published', 0)}건
⏳ <b>발행 대기</b>: {stats.get('total_pending', 0)}건
❌ <b>발행 실패</b>: {stats.get('total_failed', 0)}건
🔗 <b>내부링크</b>: {stats.get('total_links', 0)}개
📦 <b>클러스터</b>: {stats.get('total_clusters', 0)}개
━━━━━━━━━━━━━━━━"""

    return send_message(msg)


# ── 텔레그램 봇 연결 테스트 ───────────────────────────────────

def test_connection(token=None, chat_id=None):
    """텔레그램 봇 연결 테스트."""
    config = _get_config()
    tk = token or config["token"]
    cid = chat_id or config["chat_id"]

    if not tk:
        return {"ok": False, "error": "TELEGRAM_BOT_TOKEN이 설정되지 않았습니다."}
    if not cid:
        return {"ok": False, "error": "TELEGRAM_CHAT_ID가 설정되지 않았습니다."}

    # getMe로 봇 정보 확인
    result = _call_telegram_api(tk, "getMe", {})
    if result and result.get("ok"):
        bot_info = result["result"]
        # 테스트 메시지 전송
        test_msg = f"🤖 봇 연결 테스트 성공!\n봇 이름: {bot_info.get('first_name', 'Unknown')}\n시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        send_ok = send_message(test_msg, token=tk, chat_id=cid)
        return {
            "ok": True,
            "bot_name": bot_info.get("first_name", ""),
            "bot_username": bot_info.get("username", ""),
            "message_sent": send_ok
        }

    return {"ok": False, "error": "봇 API 응답 없음 또는 토큰 오류"}


# ── CLI ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Telegram Bot v1.0")
    parser.add_argument("--test", action="store_true", help="연결 테스트")
    parser.add_argument("--send", type=str, help="메시지 직접 전송")
    args = parser.parse_args()

    if args.test:
        result = test_connection()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.send:
        ok = send_message(args.send)
        print(f"전송 {'성공' if ok else '실패'}")
    else:
        parser.print_help()
