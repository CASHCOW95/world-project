import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PROFILE_CONFIG_PATH = path.join(__dirname, '../core/styler_pro_engine/publisher_profiles.json');

function createDefaultPublisherConfig() {
  return {
    global: {
      gemini_api_key: process.env.GEMINI_API_KEY || ''
    },
    profiles: [
      {
        id: 'tistory-default',
        platform: 'tistory',
        label: '기본 티스토리',
        blog_name: process.env.TISTORY_BLOG_NAME || '',
        access_token: process.env.TISTORY_ACCESS_TOKEN || '',
        enabled: true
      },
      {
        id: 'wordpress-default',
        platform: 'wordpress',
        label: '기본 워드프레스',
        api_url: process.env.WORDPRESS_API_URL || '',
        username: process.env.WORDPRESS_USER || '',
        password: process.env.WORDPRESS_PASSWORD || '',
        enabled: true
      }
    ]
  };
}

export function readPublisherConfig() {
  const defaultPublisherConfig = createDefaultPublisherConfig();
  try {
    if (!fs.existsSync(PROFILE_CONFIG_PATH)) {
      fs.writeFileSync(PROFILE_CONFIG_PATH, JSON.stringify(defaultPublisherConfig, null, 2), 'utf-8');
      return defaultPublisherConfig;
    }
    const parsed = JSON.parse(fs.readFileSync(PROFILE_CONFIG_PATH, 'utf-8'));
    return {
      global: { ...defaultPublisherConfig.global, ...(parsed.global || {}) },
      profiles: Array.isArray(parsed.profiles) ? parsed.profiles : defaultPublisherConfig.profiles
    };
  } catch (err) {
    console.error('Publisher config load failed:', err);
    return defaultPublisherConfig;
  }
}

export function writePublisherConfig(config) {
  const normalized = {
    global: {
      gemini_api_key: String(config?.global?.gemini_api_key || '')
    },
    profiles: (Array.isArray(config?.profiles) ? config.profiles : []).map((profile, index) => ({
      id: String(profile.id || `${profile.platform || 'profile'}-${Date.now()}-${index}`),
      platform: String(profile.platform || 'tistory'),
      label: String(profile.label || '새 발행 프로필'),
      blog_name: String(profile.blog_name || ''),
      access_token: String(profile.access_token || ''),
      api_url: String(profile.api_url || ''),
      username: String(profile.username || ''),
      password: String(profile.password || ''),
      enabled: profile.enabled !== false
    }))
  };
  fs.writeFileSync(PROFILE_CONFIG_PATH, JSON.stringify(normalized, null, 2), 'utf-8');
  return normalized;
}

export function getPublisherProfile(platform, profileId) {
  const config = readPublisherConfig();
  const samePlatform = config.profiles.filter(p => p.platform === platform && p.enabled !== false);
  return samePlatform.find(p => p.id === profileId) || samePlatform[0] || null;
}

export function buildPublisherEnv(platform, profileId) {
  const config = readPublisherConfig();
  const profile = getPublisherProfile(platform, profileId);
  const env = { ...process.env };

  if (config.global?.gemini_api_key) env.GEMINI_API_KEY = config.global.gemini_api_key;

  if (profile?.platform === 'tistory') {
    env.TISTORY_ACCESS_TOKEN = profile.access_token || '';
    env.TISTORY_BLOG_NAME = profile.blog_name || '';
  }
  if (profile?.platform === 'wordpress') {
    env.WORDPRESS_API_URL = profile.api_url || '';
    env.WORDPRESS_USER = profile.username || '';
    env.WORDPRESS_PASSWORD = profile.password || '';
  }
  return { env, profile };
}
