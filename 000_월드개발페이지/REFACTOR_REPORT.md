# Refactor Report

Date: 2026-06-27

## Scope

This refactor focused on structure, build stability, and cleanup. No new product features were added.

## Current Project Layout

- `frontend/`: deploy root and static HTML pages.
- `frontend/dist/`: generated deploy output.
- `frontend/workspace/`: generated local copy of the React workspace build.
- `backend/`: React/Vite workspace source, Express API server, and Python engine.
- `backend/core/components/StylerDashboard.jsx`: active React dashboard.
- `backend/core/styler_pro_engine/`: Python content/publishing engine.
- `backend/research/coin/`: research/source material separated from runtime code.
- `backend/scratch/`: research and maintenance scripts.
- `extensions/`: browser extension material.

## Completed

- Confirmed active project path is `000_월드개발페이지`.
- Excluded legacy `03_월드개발페이지` from the work target.
- Added root and backend ignore rules for dependencies, generated output, local secrets, scratch input/output, and large local tools.
- Reduced React workspace to the active dashboard path by removing unused split component/hook copies.
- Fixed backend lint to zero warnings/errors.
- Kept strict generated folders out of direct edit scope.
- Moved scratch output/input files out of `backend` root.
- Moved research material from `backend/coin` to `backend/research/coin`.
- Moved `backend/deno.exe` to `C:\dev\python_local_tools\deno.exe`.
- Documented frontend static page roles.
- Documented backend runtime/API/Python flow.
- Split publisher profile configuration helpers from `backend/server.js` into `backend/server_lib/publisherConfig.js`.
- Confirmed `cookies.txt` has no runtime code references and preserved it as auth/session material.
- Confirmed `styler_pro_x_v2.db` is the active SQLite database referenced by Python code.

## Verification

- `npm run lint` from `backend`: pass.
- `node --check backend/server.js`: pass.
- `node --check backend/server_lib/publisherConfig.js`: pass.
- `npm run build` from `frontend`: pass.
- `python -m compileall -q backend/core/styler_pro_engine backend/scratch`: pass.
- `python backend/scratch/test_cleaner.py`: pass after research path migration.
- `python backend/scratch/analyze_sung_srt.py`: pass after research path migration.

## Preserved By Design

- `backend/cookies.txt`: left in place because it may contain auth/session data.
- `.env` files: not modified.
- API URLs and auth-related code: not intentionally changed.
- `backend/research/coin/**`: retained as source material, not deleted.

## Remaining Manual Risks

- Static HTML pages still duplicate header markup. Runtime behavior is centralized only for nav active-state handling.
- `cookies.txt` still needs explicit auth cleanup approval before deletion or relocation.
- `backend/core/styler_pro_engine/styler_pro_x.db` appears unreferenced, but database cleanup still needs an explicit backup policy before moving or deleting.
- `backend/server.js` is smaller after config extraction, but route handlers can still be split later by API domain.
