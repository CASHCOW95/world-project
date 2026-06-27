import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const shimDir = path.dirname(__filename);
const repoRoot = path.resolve(shimDir, '../..');
const activeFrontendDir = path.join(repoRoot, '000_월드개발페이지/frontend');
const activeBackendDir = path.join(repoRoot, '000_월드개발페이지/backend');
const outputDir = path.join(shimDir, 'dist');

const publicPages = [
  'index.html',
  'login.html',
  'openform-download.html',
  'autohunter-download.html'
];

const protectedPages = [
  'meetup-calendar.html',
  'asset-mgmt.html',
  'profit-mgmt.html',
  'diary.html',
  'tiktok-mgmt.html',
  'timer.html',
  'online-meetup.html',
  'offline-meetup.html',
  'profile-mgmt.html',
  'gifticon-mgmt.html'
];

const staticAssetDirs = ['css', 'js', 'assets'];

function copyRecursive(src, dest) {
  if (!fs.existsSync(src)) return;
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    fs.mkdirSync(dest, { recursive: true });
    for (const item of fs.readdirSync(src)) {
      copyRecursive(path.join(src, item), path.join(dest, item));
    }
    return;
  }
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(src, dest);
}

function run(command, cwd) {
  execSync(command, { cwd, stdio: 'inherit' });
}

console.log('=== Legacy Cloudflare root shim build ===');

if (!fs.existsSync(activeFrontendDir) || !fs.existsSync(activeBackendDir)) {
  throw new Error('Active project folders were not found under 000_월드개발페이지.');
}

if (!fs.existsSync(path.join(activeBackendDir, 'node_modules'))) {
  console.log('Installing backend dependencies...');
  run('npm ci', activeBackendDir);
}

console.log('Building active React workspace...');
run('npm run build', activeBackendDir);

console.log('Writing shim dist output...');
fs.rmSync(outputDir, { recursive: true, force: true });
fs.mkdirSync(outputDir, { recursive: true });

for (const item of [...publicPages, ...protectedPages, ...staticAssetDirs]) {
  copyRecursive(path.join(activeFrontendDir, item), path.join(outputDir, item));
}

copyRecursive(path.join(activeBackendDir, 'dist'), path.join(outputDir, 'workspace'));

console.log('=== Shim build completed ===');
