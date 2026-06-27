import express from 'express';
import path from 'path';
import { spawnPython } from '../pythonProcess.js';

export function createIntegrationsRouter({ rootDir }) {
  const router = express.Router();

// 9. POST /api/telegram-test — 텔레그램 봇 연결 테스트
router.post('/telegram-test', (req, res) => {
  const { token, chat_id } = req.body;
  const scriptPath = path.join(rootDir, 'core/styler_pro_engine/telegram_bot.py');

  // 환경변수를 임시로 설정하여 테스트
  const env = { ...process.env };
  if (token) env.TELEGRAM_BOT_TOKEN = token;
  if (chat_id) env.TELEGRAM_CHAT_ID = chat_id;

  const py = spawnPython([scriptPath, '--test'], { env });
  let stdoutData = '';

  py.stdout.on('data', (data) => { stdoutData += data.toString(); });
  py.on('close', () => {
    try {
      res.json(JSON.parse(stdoutData));
    } catch {
      res.json({ ok: false, error: '응답 파싱 실패' });
    }
  });
});


  return router;
}
