import express from 'express';
import path from 'path';
import { extractMarkedJson, spawnPython } from '../pythonProcess.js';

const emptyStats = {
  total_published: 0,
  total_pending: 0,
  total_failed: 0,
  total_clusters: 0,
  total_links: 0,
  today_published: 0
};

export function createOperationsRouter({ rootDir }) {
  const router = express.Router();

  // 7. GET /api/published-posts — 발행 이력 + URL 조회
  router.get('/published-posts', (req, res) => {
    const scriptPath = path.join(rootDir, 'core/styler_pro_engine/internal_link_engine.py');

    const py = spawnPython([scriptPath, '--posts']);
    let stdoutData = '';

    py.stdout.on('data', (data) => { stdoutData += data.toString(); });
    py.on('close', () => {
      try {
        res.json(JSON.parse(stdoutData));
      } catch {
        res.json([]);
      }
    });
  });

  // 8. GET /api/internal-links — 내부링크 그래프 데이터
  router.get('/internal-links', (req, res) => {
    const scriptPath = path.join(rootDir, 'core/styler_pro_engine/internal_link_engine.py');

    const py = spawnPython([scriptPath, '--graph']);
    let stdoutData = '';

    py.stdout.on('data', (data) => { stdoutData += data.toString(); });
    py.on('close', () => {
      try {
        res.json(JSON.parse(stdoutData));
      } catch {
        res.json([]);
      }
    });
  });

  // 8.5 GET /api/dashboard-stats — 운영 대시보드 통계
  router.get('/dashboard-stats', (req, res) => {
    const scriptPath = path.join(rootDir, 'core/styler_pro_engine/internal_link_engine.py');

    const py = spawnPython([scriptPath, '--stats']);
    let stdoutData = '';

    py.stdout.on('data', (data) => { stdoutData += data.toString(); });
    py.on('close', () => {
      try {
        res.json(JSON.parse(stdoutData));
      } catch {
        res.json(emptyStats);
      }
    });
  });

  // 10. POST /api/research — 자료 수집
  router.post('/research', (req, res) => {
    const { keyword, max_news } = req.body;
    if (!keyword) {
      return res.status(400).json({ error: '키워드는 필수 입력값입니다.' });
    }
    const scriptPath = path.join(rootDir, 'core/styler_pro_engine/research_engine.py');

    const args = [scriptPath, '--keyword', keyword];
    if (max_news) args.push('--max-news', String(max_news));

    const py = spawnPython(args);
    let stdoutData = '';

    py.stdout.on('data', (data) => { stdoutData += data.toString(); });
    py.on('close', () => {
      const markedJson = extractMarkedJson(stdoutData);
      if (markedJson) {
        try {
          res.json(JSON.parse(markedJson));
        } catch {
          res.status(500).json({ error: 'JSON 파싱 오류' });
        }
      } else {
        res.json({ keyword, news: [], official_links: [], total_sources: 0, citations: [] });
      }
    });
  });

  return router;
}
