import express from 'express';
import path from 'path';
import { spawnPython } from '../pythonProcess.js';

export function createPreviewRouter({ rootDir }) {
  const router = express.Router();

router.get('/post-preview/:postId', (req, res) => {
  const postId = Number(req.params.postId);
  if (!Number.isInteger(postId) || postId <= 0) {
    return res.status(400).send('잘못된 글 번호입니다.');
  }
  const script = `
import json, re, sys
from pathlib import Path
base = Path(r"${path.join(rootDir, 'core/styler_pro_engine').replace(/\\/g, '\\\\')}")
sys.path.append(str(base))
import db, internal_link_engine
posts = internal_link_engine.get_published_posts(500)
post = next((p for p in posts if int(p.get("id", 0)) == ${postId}), None)
if not post:
    print(json.dumps({"error": "글 이력을 찾을 수 없습니다."}, ensure_ascii=False))
    raise SystemExit
content_id = None
url = post.get("url") or ""
m = re.search(r"local://content/(\\d+)", url)
if m:
    content_id = int(m.group(1))
history = db.get_history()
content = None
if content_id:
    content = next((h for h in history if int(h.get("id", 0)) == content_id), None)
if not content:
    content = next((h for h in history if h.get("title") == post.get("title")), None)
print(json.dumps({"post": post, "content": content}, ensure_ascii=False))
`.trim();

  const py = spawnPython(['-c', script]);
  let stdoutData = '';
  let stderrData = '';
  py.stdout.on('data', (data) => { stdoutData += data.toString(); });
  py.stderr.on('data', (data) => { stderrData += data.toString(); });
  py.on('close', () => {
    try {
      const payload = JSON.parse(stdoutData);
      if (payload.error || !payload.content) {
        return res.status(404).send(payload.error || '검수할 로컬 원고를 찾을 수 없습니다.');
      }
      const title = payload.content.title || payload.post.title || '작성글 검수';
      const html = payload.content.html_content || '';
      res.send(`<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${title}</title>
  <style>
    body { margin: 0; background: #0f172a; color: #0f172a; font-family: Arial, sans-serif; }
    header { position: sticky; top: 0; z-index: 10; background: #111827; color: white; padding: 14px 24px; border-bottom: 1px solid #334155; }
    header strong { display: block; font-size: 14px; }
    header span { color: #94a3b8; font-size: 12px; }
    main { max-width: 920px; margin: 24px auto; background: white; border-radius: 12px; padding: 24px; box-shadow: 0 20px 70px rgba(0,0,0,.28); }
    @media (max-width: 760px) { main { margin: 0; border-radius: 0; padding: 16px; } }
  </style>
</head>
<body>
  <header>
    <strong>내부 원고 검수</strong>
    <span>${title}</span>
  </header>
  <main>${html}</main>
</body>
</html>`);
    } catch (err) {
      res.status(500).send(`미리보기 생성 실패: ${stderrData || err.message}`);
    }
  });
});


  return router;
}
