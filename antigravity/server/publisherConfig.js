import fs from 'fs';
import path from 'path';

export function createPublisherConfigStore({ rootDir, envSource = process.env }) {
  const profileConfigPath = path.join(rootDir, 'core/styler_pro_engine/publisher_profiles.json');

  const defaultPublisherConfig = {
    global: {
      gemini_api_key: envSource.GEMINI_API_KEY || ''
    },
    profiles: [
      {
        id: 'tistory-default',
        platform: 'tistory',
        label: '기본 티스토리',
        blog_name: envSource.TISTORY_BLOG_NAME || '',
        access_token: envSource.TISTORY_ACCESS_TOKEN || '',
        enabled: true
      },
      {
        id: 'wordpress-default',
        platform: 'wordpress',
        label: '기본 워드프레스',
        api_url: envSource.WORDPRESS_API_URL || '',
        username: envSource.WORDPRESS_USER || '',
        password: envSource.WORDPRESS_PASSWORD || '',
        enabled: true
      }
    ]
  };

  function readPublisherConfig() {
    try {
      if (!fs.existsSync(profileConfigPath)) {
        fs.writeFileSync(profileConfigPath, JSON.stringify(defaultPublisherConfig, null, 2), 'utf-8');
        return defaultPublisherConfig;
      }
      const parsed = JSON.parse(fs.readFileSync(profileConfigPath, 'utf-8'));
      return {
        global: { ...defaultPublisherConfig.global, ...(parsed.global || {}) },
        profiles: Array.isArray(parsed.profiles) ? parsed.profiles : defaultPublisherConfig.profiles
      };
    } catch (err) {
      console.error('Publisher config load failed:', err);
      return defaultPublisherConfig;
    }
  }

  function writePublisherConfig(config) {
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
    fs.writeFileSync(profileConfigPath, JSON.stringify(normalized, null, 2), 'utf-8');
    return normalized;
  }

  function getPublisherProfile(platform, profileId) {
    const config = readPublisherConfig();
    const samePlatform = config.profiles.filter(p => p.platform === platform && p.enabled !== false);
    return samePlatform.find(p => p.id === profileId) || samePlatform[0] || null;
  }

  function buildPublisherEnv(platform, profileId) {
    const config = readPublisherConfig();
    const profile = getPublisherProfile(platform, profileId);
    const env = { ...envSource };

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

  return {
    profileConfigPath,
    readPublisherConfig,
    writePublisherConfig,
    getPublisherProfile,
    buildPublisherEnv
  };
}
