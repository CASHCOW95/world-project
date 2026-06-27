import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEYS = {
  style: 'styler_style_v3',
  platform: 'styler_platform_v3',
  ctaStyle: 'styler_ctaStyle_v3',
  articleLength: 'styler_articleLength_v3',
  customLength: 'styler_customLength_v3',
  faqCount: 'styler_faqCount_v3',
  generateImgPrompt: 'styler_generateImgPrompt_v3',
  seoStrength: 'styler_seoStrength_v3',
};

const DEFAULTS = {
  style: 'friendly',
  platform: 'tistory',
  ctaStyle: 'card',
  articleLength: '5000',
  customLength: '',
  faqCount: '10',
  generateImgPrompt: 'OFF',
  seoStrength: 'strong',
};

/**
 * 8개 발행 설정값의 localStorage 저장/복원을 관리하는 hook.
 * OriginalStylerDashboard와 V2AgentDashboard에서 동일하게 사용.
 */
export default function useSettings() {
  const [style, setStyle] = useState(DEFAULTS.style);
  const [platform, setPlatform] = useState(DEFAULTS.platform);
  const [ctaStyle, setCtaStyle] = useState(DEFAULTS.ctaStyle);
  const [articleLength, setArticleLength] = useState(DEFAULTS.articleLength);
  const [customLength, setCustomLength] = useState(DEFAULTS.customLength);
  const [faqCount, setFaqCount] = useState(DEFAULTS.faqCount);
  const [generateImgPrompt, setGenerateImgPrompt] = useState(DEFAULTS.generateImgPrompt);
  const [seoStrength, setSeoStrength] = useState(DEFAULTS.seoStrength);

  // Restore on mount
  useEffect(() => {
    const restore = (key, setter) => {
      const saved = localStorage.getItem(STORAGE_KEYS[key]);
      if (saved) setter(saved);
    };
    restore('style', setStyle);
    restore('platform', setPlatform);
    restore('ctaStyle', setCtaStyle);
    restore('articleLength', setArticleLength);
    restore('customLength', setCustomLength);
    restore('faqCount', setFaqCount);
    restore('generateImgPrompt', setGenerateImgPrompt);
    restore('seoStrength', setSeoStrength);
  }, []);

  // Persist on change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.style, style);
    localStorage.setItem(STORAGE_KEYS.platform, platform);
    localStorage.setItem(STORAGE_KEYS.ctaStyle, ctaStyle);
    localStorage.setItem(STORAGE_KEYS.articleLength, articleLength);
    localStorage.setItem(STORAGE_KEYS.customLength, customLength);
    localStorage.setItem(STORAGE_KEYS.faqCount, faqCount);
    localStorage.setItem(STORAGE_KEYS.generateImgPrompt, generateImgPrompt);
    localStorage.setItem(STORAGE_KEYS.seoStrength, seoStrength);
  }, [style, platform, ctaStyle, articleLength, customLength, faqCount, generateImgPrompt, seoStrength]);

  const getFinalLength = useCallback(() => {
    return articleLength === 'custom' ? customLength : articleLength;
  }, [articleLength, customLength]);

  return {
    style, setStyle,
    platform, setPlatform,
    ctaStyle, setCtaStyle,
    articleLength, setArticleLength,
    customLength, setCustomLength,
    faqCount, setFaqCount,
    generateImgPrompt, setGenerateImgPrompt,
    seoStrength, setSeoStrength,
    getFinalLength,
  };
}
