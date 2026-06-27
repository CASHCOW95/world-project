import { CATEGORY_MAP, CATEGORY_WEIGHTS, SUBCAT_WEIGHTS } from './constants';

export { CATEGORY_MAP, CATEGORY_WEIGHTS, SUBCAT_WEIGHTS };

export const formatHistoryPlatform = (platform) => (platform || 'local').toString().toUpperCase();

export const formatHistoryDate = (createdAt) => {
  const date = createdAt ? new Date(createdAt) : null;
  return date && !Number.isNaN(date.getTime()) ? date.toLocaleDateString() : '-';
};

export const normalizeHistoryItem = (item = {}) => ({
  ...item,
  platform: item.platform || 'local',
  created_at: item.created_at || null,
  title: item.title || '제목 없음',
  seo_score: item.seo_score ?? 0,
  profit_score: item.profit_score ?? 0
});

export const getStoredValue = (key, fallback) => {
  if (typeof localStorage === 'undefined') return fallback;
  const value = localStorage.getItem(key);
  return value || fallback;
};

export const getSortedSubCategories = (categories, mainCategory) => {
  const source = categories?.[mainCategory]
    ? Object.keys(categories[mainCategory])
    : CATEGORY_MAP[mainCategory] || [];

  return [...source].sort((a, b) => (SUBCAT_WEIGHTS[b] || 0) - (SUBCAT_WEIGHTS[a] || 0));
};
