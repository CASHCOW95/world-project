# World Development Page AGENTS.md

This project contains the deployable web page and the React/Vite dashboard source.
It inherits root rules from `../AGENTS.md`.

## Read Order

1. `../AGENTS.md`
2. `../README.md`
3. `backend/design_guide.md` when changing UI/design
4. `backend/adsense_money_keyword.md` only for keyword/revenue-content work
5. Relevant source files under `backend` or `frontend`

## Structure

- Deploy root: `frontend`
- Integrated build command: run `npm run build` from `frontend`
- React/Vite source and API package: `backend`
- Static deploy output is generated into `frontend/dist`
- Legacy material should stay under `../legacy`

## Rules

- Keep Cloudflare Pages settings aligned with root `README.md`.
- Do not edit generated `dist` output directly unless the user asks for emergency static output patching.
- Use `backend/design_guide.md` for landing-page visual direction.
- Large research docs under `backend/research/coin` are references; read only the relevant one.

## Verification

- For deployment changes, run `npm run build` from `frontend`.
- For backend source changes, run the relevant `backend` build or lint command when dependencies are available.
