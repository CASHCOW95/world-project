import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const frontendDir = __dirname;
const backendDir = path.join(frontendDir, '../backend');
const distDir = path.join(frontendDir, 'dist');
const publicPages = [
  'index.html',
  'login.html',
  'openform-download.html',
  'autohunter-download.html',
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
  'gifticon-mgmt.html',
];
const staticAssetDirs = ['css', 'js', 'assets'];

console.log('=== Starting Build Process ===');

// 1. Build React App in backend
console.log('Building React Styler Pro X...');
try {
  // Check if node_modules exists, if not, do npm install / npm ci
  if (!fs.existsSync(path.join(backendDir, 'node_modules'))) {
    console.log('Installing backend dependencies (npm ci)...');
    execSync('npm ci', { cwd: backendDir, stdio: 'inherit' });
  }
  console.log('Running npm run build inside backend...');
  execSync('npm run build', { cwd: backendDir, stdio: 'inherit' });
} catch (err) {
  console.error('Failed to build React app:', err);
  process.exit(1);
}

// 2. Clean and create dist directory
console.log('Cleaning dist directory...');
if (fs.existsSync(distDir)) {
  fs.rmSync(distDir, { recursive: true, force: true });
}
fs.mkdirSync(distDir);

// 3. Copy static pages and folders
console.log('Copying static frontend assets to dist...');
const itemsToCopy = [...publicPages, ...protectedPages, ...staticAssetDirs];

for (const item of itemsToCopy) {
  const src = path.join(frontendDir, item);
  const dest = path.join(distDir, item);
  if (fs.existsSync(src)) {
    fs.cpSync(src, dest, { recursive: true });
  }
}

// 4. Copy built React files to dist/workspace
console.log('Copying built React app to dist/workspace...');
const reactBuildDir = path.join(backendDir, 'dist');
const destWorkspaceDir = path.join(distDir, 'workspace');

if (fs.existsSync(reactBuildDir)) {
  fs.cpSync(reactBuildDir, destWorkspaceDir, { recursive: true });
} else {
  console.error('React build output not found at:', reactBuildDir);
  process.exit(1);
}

console.log('=== Build Completed Successfully! ===');
