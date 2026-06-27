# Backend Runtime

`backend` contains the React/Vite workspace source, the local Express API server, and the Python content engine.

## Main Commands

- `npm run dev`: Vite dev server for the React workspace.
- `npm run server`: Express API server.
- `npm run dev:all`: Vite and Express together.
- `npm run build`: builds the React workspace into `backend/dist`.
- `npm run lint`: ESLint for backend JavaScript and React source.

## Runtime Entry Points

- `server.js`: Express server and API gateway.
- `server_lib/publisherConfig.js`: publisher profile configuration reader/writer and environment builder.
- `core/main.jsx`: React workspace browser entry.
- `core/components/StylerDashboard.jsx`: active React dashboard implementation.
- `core/styler_pro_engine/main.py`: single-post and cluster publishing pipeline.

## API To Python Flow

`server.js` shells out to Python scripts under `core/styler_pro_engine` for keyword search, title generation, history, publishing, cluster generation, internal links, Telegram tests, and research helpers.

Important routes:

- `GET /api/categories`
- `GET /api/keywords`
- `POST /api/generate-titles`
- `GET /api/history`
- `POST /api/publish-pipeline`
- `POST /api/cluster-generate`
- `POST /api/cluster-publish`
- `GET /api/published-posts`
- `GET /api/internal-links`
- `GET /api/dashboard-stats`
- `POST /api/telegram-test`
- `POST /api/research`

## Data And Generated Files

- `core/styler_pro_engine/*.db`: local SQLite runtime data.
- `core/styler_pro_engine/publisher_profiles.json`: publisher profile configuration.
- `web_dashboard/output/`: generated article/image output, ignored by git.
- `dist/` and `deploy/`: generated build/deploy output, ignored by git.
- `scratch/`: research and maintenance scripts, not runtime code.
- `research/coin/`: source research material moved out of the runtime root.

## Sensitive Files

- `cookies.txt` may contain auth/session material. Do not edit, move, or delete it during refactors unless explicitly requested.
- `.env` files are ignored and should not be modified during structural cleanup.
