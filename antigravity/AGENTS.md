# AGENTS.md

This project is the Styler Pro X / AI blog automation dashboard and backend.
It lives under the mixed `C:\dev\python` workspace, so confirm the target folder
before changing files.

## Read Order

1. `AGENTS.md`
2. `GEMINI.md`
3. `project.md`
4. `docs/refactor_audit.md` when doing cleanup, deletion review, or structural refactoring
5. `docs/benchmarking_analysis.md` only when changing strategy, content quality, SEO, or publishing logic
6. Relevant source files under `core`, `core/hooks`, `core/components`, or `core/styler_pro_engine`

## Structure

- Frontend source: `core/`
- Active frontend entry: `index.html` -> `core/main.jsx` -> `core/App.jsx` -> `core/components/StylerDashboard.jsx`
- Shared React components: `core/components/shared/`
- Frontend hooks: `core/hooks/`
- Python content engine: `core/styler_pro_engine/`
- Node/Express server: `server.js`
- Runtime/static output: `web_dashboard/output/`

## Current Refactor State

- `core/components/StylerDashboard.jsx` is the active dashboard wrapper and mode switcher.
- `core/components/OriginalStylerDashboard.jsx` and
  `core/components/V2AgentDashboard.jsx` are wired into the active dashboard path.
- `core/components/StylerDashboard.css` owns the extracted dashboard styles.
- `server.js` owns Express setup, static serving, route mounting, and process startup.
- API route groups live under `server/routes/`; Python process helpers live in
  `server/pythonProcess.js`.

## Rules

- Do not add new features during refactoring.
- Preserve existing API routes, request shapes, environment variable names, and auth/publishing settings.
- Do not edit `.env`, API addresses, tokens, publisher credentials, local DB files, or generated publishing output unless explicitly requested.
- Prefer source edits under `core/` over direct generated-output edits.
- Keep changes staged by phase: documentation, lint/config, frontend extraction, backend extraction, Python cleanup, artifact deletion.
- Any file deletion needs a listed reason first.

## Verification

- Run `npm run build` after frontend or config changes when possible.
- Run `npm run lint` after lint/config or JavaScript changes; known baseline may fail during early refactor phases.
- Run `node --check server.js` after backend changes.
- Syntax-check touched Python files with `python -m py_compile`.
- For API/server changes, verify the affected endpoint or document why it could not be run.
