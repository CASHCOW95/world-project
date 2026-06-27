import express from 'express';
import fs from 'fs';
import path from 'path';
import { extractMarkedJson, spawnPython } from '../pythonProcess.js';

export function createContentPlanningRouter({ rootDir }) {
  const router = express.Router();

  // 0. GET /api/categories
  router.get('/categories', (req, res) => {
    const categoriesPath = path.join(rootDir, 'core/styler_pro_engine/categories.json');
    try {
      const data = fs.readFileSync(categoriesPath, 'utf8');
      res.json(JSON.parse(data));
    } catch (err) {
      console.error("Failed to read categories.json:", err);
      res.status(500).json({ error: "카테고리 정보를 로드할 수 없습니다." });
    }
  });

  // 1. GET /api/keywords
  router.get('/keywords', (req, res) => {
    const { category } = req.query;
    const scriptPath = path.join(rootDir, 'core/styler_pro_engine/keyword_finder.py');

    const py = spawnPython([scriptPath, category || '생활']);
    let stdoutData = '';
    let stderrData = '';

    py.stdout.on('data', (data) => {
      stdoutData += data.toString();
    });

    py.stderr.on('data', (data) => {
      stderrData += data.toString();
    });

    py.on('close', (code) => {
      if (code !== 0) {
        console.error(`Keyword analyzer crashed: ${stderrData}`);
        return res.status(500).json({ error: '키워드 분석기 실행 실패', details: stderrData });
      }
      try {
        const parsed = JSON.parse(stdoutData);
        res.json(parsed);
      } catch (err) {
        res.status(500).json({ error: 'JSON 파싱 실패', details: err.message, raw: stdoutData });
      }
    });
  });

  // 1.5 POST /api/generate-titles
  router.post('/generate-titles', (req, res) => {
    const { keyword, category } = req.body;
    if (!keyword) {
      return res.status(400).json({ error: "키워드는 필수 입력값입니다." });
    }
    const scriptPath = path.join(rootDir, 'core/styler_pro_engine/title_generator.py');

    const py = spawnPython([scriptPath, '--keyword', keyword, '--category', category || '정부지원금']);
    let stdoutData = '';
    let stderrData = '';

    py.stdout.on('data', (data) => {
      stdoutData += data.toString();
    });

    py.stderr.on('data', (data) => {
      stderrData += data.toString();
    });

    py.on('close', (code) => {
      if (code !== 0) {
        console.error(`Title generator crashed with code ${code}: ${stderrData}`);
        return res.status(500).json({ error: '제목 생성기 작동 중 에러 발생', details: stderrData });
      }

      const markedJson = extractMarkedJson(stdoutData);
      if (markedJson) {
        try {
          const parsed = JSON.parse(markedJson);
          res.json(parsed);
        } catch (err) {
          res.status(500).json({ error: 'JSON 파싱 오류', details: err.message, raw: stdoutData });
        }
      } else {
        res.status(500).json({ error: '결과 데이터 마커 누락' });
      }
    });
  });

  // 2. GET /api/history
  router.get('/history', (req, res) => {
    const scriptPath = path.join(rootDir, 'core/styler_pro_engine/db.py');

    const py = spawnPython([scriptPath, '--history']);
    let stdoutData = '';
    let stderrData = '';

    py.stdout.on('data', (data) => {
      stdoutData += data.toString();
    });

    py.stderr.on('data', (data) => {
      stderrData += data.toString();
    });

    py.on('close', (code) => {
      if (code !== 0) {
        console.error(`DB history crashed: ${stderrData}`);
        return res.status(500).json({ error: '발행 이력 로드 실패', details: stderrData });
      }
      try {
        const parsed = JSON.parse(stdoutData);
        res.json(parsed);
      } catch (err) {
        res.status(500).json({ error: 'JSON 파싱 실패', details: err.message });
      }
    });
  });

  return router;
}
