# Frontend Static Pages

The `frontend` folder is the deploy root. `npm run build` copies these static pages into `frontend/dist` and copies the React/Vite workspace build into `frontend/dist/workspace`.

## Public Pages

- `index.html`: main landing/dashboard entry.
- `login.html`: local admin login gate.
- `openform-download.html`: public OpenForm download page.
- `autohunter-download.html`: public AUTOmaple download page.

## Protected Pages

These pages are guarded by `js/main.js` through `sessionStorage.isAdminLoggedIn`.

- `meetup-calendar.html`
- `asset-mgmt.html`
- `profit-mgmt.html`
- `diary.html`
- `tiktok-mgmt.html`
- `timer.html`
- `online-meetup.html`
- `offline-meetup.html`
- `profile-mgmt.html`
- `gifticon-mgmt.html`

## Workspace

- `workspace/` is generated during build from `backend/dist`.
- Do not edit `frontend/workspace` or `frontend/dist` directly.

## Route Notes

- `index.html` links directly to the primary cards: meetup calendar, asset management, profit management, diary, TikTok management, OpenForm, AUTOmaple, and the React workspace.
- `online-meetup.html`, `offline-meetup.html`, `profile-mgmt.html`, `gifticon-mgmt.html`, and `timer.html` are protected utility pages. They are copied for direct/admin access even if they are not primary cards on `index.html`.
