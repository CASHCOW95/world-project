# Refactor Audit

Date: 2026-06-27
Target: `C:\dev\python\antigravity`
Backup: `C:\dev\python_backup`

This document records the current cleanup/refactor baseline. It is intentionally
limited to structural findings and verification results; it does not define new
features.

## Project Role Map

| Area | Path | Role |
|---|---|---|
| Frontend app | `core/` | React/Vite dashboard source |
| Active frontend entry | `index.html` -> `core/main.jsx` -> `core/App.jsx` -> `core/components/StylerDashboard.jsx` | Current mounted dashboard path |
| Split frontend components | `core/components/OriginalStylerDashboard.jsx`, `core/components/V2AgentDashboard.jsx`, `core/hooks/`, `core/components/shared/` | Refactor structure used by the active dashboard wrapper |
| Dashboard stylesheet | `core/components/StylerDashboard.css` | Extracted global dashboard CSS previously embedded in the wrapper component |
| Backend | `server.js` | Express API server bootstrap, static serving, and route mounting |
| Backend modules | `server/publisherConfig.js`, `server/pythonProcess.js`, `server/routes/*.js` | Publisher profile store/router, content planning, operations, generation, preview, publishing/export, integrations, and Python process helpers extracted from `server.js` |
| Python engine | `core/styler_pro_engine/` | Keyword, title, content, publishing, research, cluster, and link engines |
| Static/runtime output | `web_dashboard/output/` | Generated output and images served by the backend |
| Build output | `dist/` | Vite production build output |
| Docs | `GEMINI.md`, `project.md`, `docs/benchmarking_analysis.md`, `docs/refactor_audit.md` | Project context, work log, strategy reference, and cleanup baseline |
| Config | `package.json`, `vite.config.js`, `eslint.config.js`, `tailwind.config.js`, `postcss.config.js` | Node/Vite/Tailwind/ESLint configuration |

## Entry Points and Commands

- Frontend dev: `npm run dev`
- Backend dev: `npm run server`
- Combined dev: `npm run dev:all`
- Production build: `npm run build`
- Lint: `npm run lint`
- Backend port: `process.env.PORT || 5000`
- Backend smoke endpoint: `GET /api/`

## Current Verification Baseline

- `npm run build`: passes.
- `npm run lint`: passes with 0 warnings after phase 7 cleanup.
- `node --check server.js`, `server/*.js`, and `server/routes/*.js`: passes.
- `python -m py_compile` for all `core/styler_pro_engine/*.py`: passes.
- `npm run server`: starts successfully.
- `GET http://localhost:5000/api/`: returns `ok: true`.
- `GET http://localhost:5000/api/credits`: returns generation credit state.
- `GET http://localhost:5000/api/categories`: returns category data.
- `GET http://localhost:5000/api/keywords`: returns keyword candidates.
- `POST http://localhost:5000/api/generate-titles`: returns generated title candidates.
- `GET http://localhost:5000/api/history`: returns history data.
- `GET http://localhost:5000/api/publisher-profiles`: returns publisher profile metadata without exposing values in reports.
- `GET http://localhost:5000/api/dashboard-stats`: returns Python-backed dashboard stats.
- `GET http://localhost:5000/api/published-posts`: returns published post metadata.
- `GET http://localhost:5000/api/internal-links`: returns internal link graph data.
- `POST http://localhost:5000/api/research`: returns research sources.
- Publishing, export, Gemini generation, and Telegram send/test routes were not
  invoked during smoke testing because they can touch external services,
  generate content, or trigger publishing workflows.

Latest lint baseline after phase 5:

- 0 warnings, 0 errors.
- Remaining `react-hooks/set-state-in-effect` warnings were removed by moving
  category selection and effect-triggered loading into explicit handlers and
  local loaders.
- `core/components/OriginalStylerDashboard.jsx`,
  `core/components/V2AgentDashboard.jsx`, `core/hooks/useCategories.js`, and
  hook dependency warnings have been cleaned up for the current lint
  configuration.

Phase 4 structural changes:

- The active dashboard implementation was split out of
  `core/components/StylerDashboard.jsx`.
- `core/components/StylerDashboard.jsx` is now the wrapper, theme CSS host, and
  mode switcher.
- `core/components/OriginalStylerDashboard.jsx` now contains the active
  "원고 자동 집필기" implementation extracted from the monolith.
- `core/components/V2AgentDashboard.jsx` now contains the active V2 operator
  implementation extracted from the monolith.
- `core/components/dashboardUtils.js` holds common category/history/localStorage
  helpers shared by the extracted dashboards.

Phase 5 lint cleanup:

- `core/components/dashboardUtils.js` now also exposes
  `getSortedSubCategories` for shared subcategory ordering.
- Original and V2 dashboard category changes now go through
  `handleMainCategoryChange` instead of relying on a state-sync effect.
- Keyword and tab data loading effects use local async loaders instead of
  calling external state-changing callbacks from the effect body.
- Unused original-mode publisher profile form/config state was removed; the
  original mode now keeps only the selected publisher profile id required for
  pipeline requests.

Phase 6 DOM patch cleanup:

- Removed the `StylerDashboard.jsx` effect that scanned rendered DOM with
  `querySelectorAll`, patched inline styles with `style.setProperty`, and
  re-ran through `MutationObserver`.
- Removed the dead `ThemeToggleButton` placeholder and unused `themeMode`
  state.
- Removed CSS classes that were only applied by the deleted DOM patching code.
- Extracted the large embedded dashboard style string from
  `StylerDashboard.jsx` into `core/components/StylerDashboard.css`.
- Kept the fetch stream log normalizer because it changes API stream text, not
  layout.

Phase 7 CSS cleanup:

- Removed unused dashboard CSS selectors left behind by previous DOM patching,
  history modal experiments, and unused SaaS/upbit force classes.
- Removed overwritten duplicate font-size, light-theme background, input, border,
  and slate/gray background rules.
- Parsed `core/components/StylerDashboard.css` with PostCSS after cleanup:
  62 rules, 294 lines, 0 duplicate selectors.
- Preserved the current dark-mode default and kept the active `lg:col-span-*`
  layout overrides used by the extracted original dashboard.

Phase 8 server split:

- Extracted publisher profile file I/O and environment construction into
  `server/publisherConfig.js`.
- Extracted `/api/publisher-profiles` routes into
  `server/routes/publisherProfiles.js`.
- Kept existing environment variable names, API paths, response messages, and
  `core/styler_pro_engine/publisher_profiles.json` path unchanged.
- Expanded ESLint's Node target from only `server.js` to
  `server.js` plus `server/**/*.js`.

Phase 9 Python process helper split:

- Added `server/pythonProcess.js` for shared Python command selection and
  `spawnPython()` process creation.
- Moved repeated `---JSON_START---` / `---JSON_END---` marker extraction into
  `extractMarkedJson()`.
- Replaced direct Python command selection in `server.js` with `spawnPython()`
  while keeping script paths, arguments, API routes, and response formats
  unchanged.
- Verified a Python-backed read endpoint through `/api/dashboard-stats`.

Phase 10 content planning route split:

- Extracted `/api/categories`, `/api/keywords`, `/api/generate-titles`, and
  `/api/history` into `server/routes/contentPlanning.js`.
- Kept existing API paths, Python script paths, request defaults, response
  messages, and error payload shapes unchanged.
- Verified the moved file-backed and Python-backed endpoints after extraction.

Phase 11 operations route split:

- Extracted `/api/published-posts`, `/api/internal-links`,
  `/api/dashboard-stats`, and `/api/research` into
  `server/routes/operations.js`.
- Kept existing API paths, Python script paths, fallback response shapes, and
  request defaults unchanged.
- Left `/api/telegram-test` in `server.js` for now because it handles
  user-supplied notification credentials.

Phase 12 server route final split:

- Extracted `/api/credits`, `/api/credits/reset`, and `/api/generate` into
  `server/routes/generation.js`.
- Extracted `/api/post-preview/:postId` into `server/routes/preview.js`.
- Extracted `/api/publish-pipeline`, `/api/export-download`,
  `/api/cluster-generate`, and `/api/cluster-publish` into
  `server/routes/publishing.js`.
- Extracted `/api/telegram-test` into `server/routes/integrations.js`.
- Reduced `server.js` to environment loading, Express setup, static serving,
  publisher environment wiring, route mounting, and `app.listen()`.
- Kept API paths, Python script paths, streaming behavior, response payload
  shapes, and environment variable names unchanged.
- Verified syntax/lint/build and safe API smoke endpoints after extraction.

Phase 13 Python engine review:

- Confirmed server-launched Python entry points:
  `main.py`, `cluster_engine.py`, `internal_link_engine.py`,
  `research_engine.py`, `telegram_bot.py`, `keyword_finder.py`,
  `title_generator.py`, and `db.py`.
- Confirmed `main.py` imports the active generation/publishing pipeline modules:
  `serp_analyzer.py`, `content_builder.py`, `cta_engine.py`,
  `image_factory.py`, `image_generator.py`, `html_block_engine.py`,
  `revenue_score_engine.py`, `seo_engine.py`, `export_engine.py`,
  `publisher.py`, `cluster_engine.py`, `randomizer_engine.py`,
  `research_engine.py`, `internal_link_engine.py`, `telegram_bot.py`, and
  `content_qa.py`.
- Identified standalone CLI-only review candidates with no server/main import:
  `keyword_analyzer.py`, `profit_evaluator.py`, `seo_evaluator.py`, and
  `competitor_analyzer.py`.
- Did not delete those standalone CLI files because each has an executable
  `__main__` path and deleting them could remove existing utility behavior.
- Re-ran Python syntax checks for all engine files and removed generated
  `__pycache__` after verification.

## Known Structural Issues

1. `core/components/StylerDashboard.css` still contains broad light-theme compatibility rules even though the wrapper currently forces dark mode.
2. Publishing, export, Gemini generation, and Telegram integration routes are now modularized but still need manual/live validation before any real external publishing or notification run.
3. The previous `.agents/AGENTS.md` content described YouTube crawling, which did not match this project. It now delegates to project-level `AGENTS.md`.
4. `docs/benchmarking_analysis.md` duplicates the root `C:\dev\python\docs\benchmarking_analysis.md` content.
5. Remaining light-theme CSS should be reviewed only after deciding whether a light mode is still a supported path.
6. `keyword_analyzer.py`, `profit_evaluator.py`, `seo_evaluator.py`, and `competitor_analyzer.py` appear to be standalone legacy/utility CLIs, not active API pipeline dependencies.

## Cleanup Candidates

Removed safe cleanup candidates:

- `dev-server.err.log`
- `dev-server.out.log`
- `temp_test.log`
- `temp_test2.log`
- `core/styler_pro_engine/__pycache__/`
- `youtube_results.csv`
- `merge_dashboards.cjs`

Review-before-delete candidates:

- Duplicate `docs/benchmarking_analysis.md`; keep one canonical copy only after confirming routing expectations.
- `core/styler_pro_engine/keyword_analyzer.py`, `profit_evaluator.py`,
  `seo_evaluator.py`, and `competitor_analyzer.py` only after confirming no one
  uses their standalone CLI behavior.

Protected files and paths:

- `.env`
- API URLs, auth tokens, publishing credentials, and related settings
- `core/styler_pro_engine/publisher_profiles.json`
- `core/styler_pro_engine/styler_pro_x.db`
- `core/styler_pro_engine/styler_pro_x_v2.db`
- `web_dashboard/output/`

## Refactor Phases

1. Establish project-local instructions and audit baseline.
2. Remove approved temporary artifacts only.
3. Fix ESLint environment/config issues without changing runtime behavior.
4. Reduce active frontend monolith by extracting from `StylerDashboard.jsx` into the already planned hook/component structure.
5. Reduce remaining React lint debt in the extracted dashboard components.
6. Remove direct DOM layout patching from the active dashboard wrapper.
7. De-duplicate and scope `core/components/StylerDashboard.css` without changing the current dark-mode default.
8. Split publisher profile handling out of `server.js` while preserving API routes and environment names.
9. Extract Python process helpers from `server.js`.
10. Split content planning routes out of `server.js`.
11. Split operations routes out of `server.js`.
12. Split publishing/export/preview/Gemini/Telegram route groups out of `server.js`.
13. Review Python engine modules and keep standalone CLI utilities until their external usage is explicitly ruled out.
