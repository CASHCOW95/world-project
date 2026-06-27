import express from 'express';
import fs from 'fs';
import path from 'path';
import { extractMarkedJson, spawnPython } from '../pythonProcess.js';

export function createPublishingRouter({ rootDir, buildPublisherEnv }) {
  const router = express.Router();

// 3. POST /api/publish-pipeline (Streaming log via chunked SSE)
router.post('/publish-pipeline', (req, res) => {
  const { keyword, platform, profile_id, style, search_volume, competition, cpc, category, cta_style, golden_score, length, faq_count, img_prompt, title, seo_strength, publish } = req.body;
  
  if (!keyword) {
    return res.status(400).json({ error: '키워드는 필수 입력값입니다.' });
  }

  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
  });
  const scriptPath = path.join(rootDir, 'core/styler_pro_engine/main.py');
  
  const args = [
    scriptPath,
    '--keyword', keyword,
    '--platform', platform || 'tistory',
    '--style', style || 'friendly',
    '--search_volume', String(search_volume || 10000),
    '--competition', String(competition || 5000),
    '--cpc', cpc || '보통',
    '--category', category || '생활',
    '--cta_style', cta_style || 'card',
    '--golden_score', String(golden_score || 80),
    '--length', String(length || '5000'),
    '--faq_count', String(faq_count || '10'),
    '--img_prompt', String(img_prompt || 'OFF'),
    '--title', title || '',
    '--seo_strength', seo_strength || 'strong',
    '--publish', publish ? 'ON' : 'OFF'
  ];



  const { env, profile } = buildPublisherEnv(platform || 'tistory', profile_id);
  if (profile) {
    res.write(`data: ${JSON.stringify({ log: `[PROFILE] ${profile.label} 프로필로 발행 환경을 준비했습니다.` })}\n\n`);
  }
  const py = spawnPython(args, { env });
  let stdoutData = '';
  
  py.stdout.on('data', (data) => {
    const chunk = data.toString();
    stdoutData += chunk;
    
    const lines = chunk.split('\n');
    lines.forEach(line => {
      if (line.trim()) {
        res.write(`data: ${JSON.stringify({ log: line.trim() })}\n\n`);
      }
    });
  });

  py.stderr.on('data', (data) => {
    const errLine = data.toString().trim();
    console.error(`[Python Engine Error] ${errLine}`);
    res.write(`data: ${JSON.stringify({ log: `⚠️ [에러] ${errLine}` })}\n\n`);
  });

  py.on('close', (code) => {
    if (code !== 0) {
      res.write(`data: ${JSON.stringify({ error: '파이프라인 프로세스 비정상 종료' })}\n\n`);
      res.end();
      return;
    }
    
    const markedJson = extractMarkedJson(stdoutData);
    if (markedJson) {
      try {
        const finalJson = JSON.parse(markedJson);
        res.write(`data: ${JSON.stringify({ success: true, result: finalJson })}\n\n`);
      } catch {
        res.write(`data: ${JSON.stringify({ error: '최종 결과 데이터 파싱 오류', raw: markedJson })}\n\n`);
      }
    } else {
      res.write(`data: ${JSON.stringify({ error: '최종 결과 데이터 마커 누락' })}\n\n`);
    }
    res.end();
  });
});

// 4. GET /api/export-download (ZIP compression and download of exported assets)
router.get('/export-download', (req, res) => {
  const outputDir = path.join(rootDir, 'web_dashboard/output');
  const zipPath = path.join(rootDir, 'web_dashboard/styler_pro_export.zip');

  // Python code block to zip the output directory recursively
  const zipCmd = `
import zipfile, os
zip_path = r"${zipPath.replace(/\\/g, '\\\\')}"
output_dir = r"${outputDir.replace(/\\/g, '\\\\')}"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, output_dir)
            zipf.write(file_path, arcname)
`.trim().replace(/\r?\n/g, '; ');

  const py = spawnPython(['-c', zipCmd]);

  py.on('close', (code) => {
    if (code !== 0) {
      console.error(`Zip creation failed with exit code ${code}`);
      return res.status(500).json({ error: 'Zip 압축 파일 생성 중 에러가 발생했습니다.' });
    }
    
    res.download(zipPath, 'styler_pro_export.zip', (err) => {
      if (err) {
        console.error('Download error:', err);
      }
      // Clean up the temporary zip file
      try {
        fs.unlinkSync(zipPath);
      } catch (e) {
        console.error('Failed to delete zip file:', e);
      }
    });
  });
});

// ═══════════════════════════════════════════════════════
// V2 API: AI 블로그 운영 에이전트 신규 엔드포인트
// ═══════════════════════════════════════════════════════

// 5. POST /api/cluster-generate — 클러스터 구조 미리보기 생성
router.post('/cluster-generate', (req, res) => {
  const { keyword, category, min_subs, max_subs } = req.body;
  if (!keyword) {
    return res.status(400).json({ error: '키워드는 필수 입력값입니다.' });
  }
  const scriptPath = path.join(rootDir, 'core/styler_pro_engine/cluster_engine.py');

  const args = [scriptPath, '--keyword', keyword, '--category', category || '정보형'];
  if (min_subs) args.push('--min-subs', String(min_subs));
  if (max_subs) args.push('--max-subs', String(max_subs));

  const py = spawnPython(args);
  let stdoutData = '';
  let stderrData = '';

  py.stdout.on('data', (data) => { stdoutData += data.toString(); });
  py.stderr.on('data', (data) => { stderrData += data.toString(); });

  py.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).json({ error: '클러스터 생성 실패', details: stderrData });
    }
    const markedJson = extractMarkedJson(stdoutData);
    if (markedJson) {
      try {
        res.json(JSON.parse(markedJson));
      } catch (err) {
        res.status(500).json({ error: 'JSON 파싱 오류', details: err.message });
      }
    } else {
      res.status(500).json({ error: '결과 데이터 마커 누락' });
    }
  });
});

// 6. POST /api/cluster-publish — 클러스터 전체 순차 발행 (SSE 스트리밍)
router.post('/cluster-publish', (req, res) => {
  const { keyword, category, platform, profile_id, style, length, faq_count, img_prompt,
          seo_strength, publish, min_subs, max_subs, search_volume, competition, cpc,
          scheduled_at, contextual_links } = req.body;

  if (!keyword) {
    return res.status(400).json({ error: '키워드는 필수 입력값입니다.' });
  }

  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
  });
  const scriptPath = path.join(rootDir, 'core/styler_pro_engine/main.py');

  const args = [
    scriptPath,
    '--mode', 'cluster',
    '--keyword', keyword,
    '--category', category || '정보형',
    '--platform', platform || 'tistory',
    '--style', style || 'friendly',
    '--length', String(length || '5000'),
    '--faq_count', String(faq_count || '10'),
    '--img_prompt', String(img_prompt || 'OFF'),
    '--seo_strength', seo_strength || 'strong',
    '--publish', publish ? 'ON' : 'OFF',
    '--search_volume', String(search_volume || 10000),
    '--competition', String(competition || 5000),
    '--cpc', cpc || '보통',
    '--min_subs', String(min_subs || 3),
    '--max_subs', String(max_subs || 10),
  ];

  if (scheduled_at) {
    args.push('--scheduled_at', String(scheduled_at));
  }
  if (contextual_links) {
    args.push('--contextual_links', String(contextual_links));
  }

  const { env, profile } = buildPublisherEnv(platform || 'tistory', profile_id);
  if (profile) {
    res.write(`data: ${JSON.stringify({ log: `[PROFILE] ${profile.label} 프로필로 발행 환경을 준비했습니다.` })}\n\n`);
  }
  const py = spawnPython(args, { env });
  let stdoutData = '';

  py.stdout.on('data', (data) => {
    const chunk = data.toString();
    stdoutData += chunk;
    const lines = chunk.split('\n');
    lines.forEach(line => {
      if (line.trim()) {
        res.write(`data: ${JSON.stringify({ log: line.trim() })}\n\n`);
      }
    });
  });

  py.stderr.on('data', (data) => {
    const errLine = data.toString().trim();
    console.error(`[Cluster Engine Error] ${errLine}`);
    res.write(`data: ${JSON.stringify({ log: `⚠️ [에러] ${errLine}` })}\n\n`);
  });

  py.on('close', (code) => {
    if (code !== 0) {
      res.write(`data: ${JSON.stringify({ error: '클러스터 파이프라인 비정상 종료' })}\n\n`);
      res.end();
      return;
    }
    const markedJson = extractMarkedJson(stdoutData);
    if (markedJson) {
      try {
        const finalJson = JSON.parse(markedJson);
        res.write(`data: ${JSON.stringify({ success: true, result: finalJson })}\n\n`);
      } catch {
        res.write(`data: ${JSON.stringify({ error: '결과 파싱 오류' })}\n\n`);
      }
    } else {
      res.write(`data: ${JSON.stringify({ error: '결과 데이터 마커 누락' })}\n\n`);
    }
    res.end();
  });
});


  return router;
}
