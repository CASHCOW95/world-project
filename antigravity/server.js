import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { createPublisherConfigStore } from './server/publisherConfig.js';
import { createPublisherProfilesRouter } from './server/routes/publisherProfiles.js';
import { createContentPlanningRouter } from './server/routes/contentPlanning.js';
import { createOperationsRouter } from './server/routes/operations.js';
import { createGenerationRouter } from './server/routes/generation.js';
import { createPreviewRouter } from './server/routes/preview.js';
import { createPublishingRouter } from './server/routes/publishing.js';
import { createIntegrationsRouter } from './server/routes/integrations.js';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 5000;

app.get('/api/', (req, res) => {
  res.json({
    ok: true,
    message: 'API server is running. Open /workspace/index.html?view=styler for the dashboard.'
  });
});

app.use(cors());
app.use(express.json());

// 포털 메인 및 빌드된 리액트 워크스페이스 정적 웹 호스팅 서비스 추가
app.use('/workspace', express.static(path.join(__dirname, '../03_월드개발페이지/frontend/dist/workspace')));
app.use('/output', express.static(path.join(__dirname, 'web_dashboard/output')));
app.use(express.static(path.join(__dirname, '../03_월드개발페이지/frontend/dist')));

const publisherConfigStore = createPublisherConfigStore({ rootDir: __dirname });
const { buildPublisherEnv } = publisherConfigStore;
app.use('/api/publisher-profiles', createPublisherProfilesRouter(publisherConfigStore));
app.use('/api', createContentPlanningRouter({ rootDir: __dirname }));
app.use('/api', createOperationsRouter({ rootDir: __dirname }));
app.use('/api', createGenerationRouter());
app.use('/api', createPreviewRouter({ rootDir: __dirname }));
app.use('/api', createPublishingRouter({ rootDir: __dirname, buildPublisherEnv }));
app.use('/api', createIntegrationsRouter({ rootDir: __dirname }));

app.listen(PORT, () => {
  console.log(`AI Blog Agent Backend running on http://localhost:${PORT}`);
});
