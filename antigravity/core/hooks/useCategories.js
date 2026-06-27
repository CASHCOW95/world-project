import { useState, useEffect, useMemo, useCallback } from 'react';
import { CATEGORY_MAP, CATEGORY_WEIGHTS, SUBCAT_WEIGHTS } from '../components/constants';

const getSortedSubCategories = (source, mainCategory) => {
  const subCats = source[mainCategory]
    ? Object.keys(source[mainCategory])
    : (CATEGORY_MAP[mainCategory] || []);
  return [...subCats].sort(
    (a, b) => (SUBCAT_WEIGHTS[b] || 0) - (SUBCAT_WEIGHTS[a] || 0)
  );
};

/**
 * 카테고리 로드 및 mainCategory ↔ subCategory 연동 로직을 관리하는 hook.
 */
export default function useCategories() {
  const [categories, setCategories] = useState({});
  const [mainCategory, setMainCategoryState] = useState('정부정책');
  const [subCategory, setSubCategory] = useState('정부지원금');

  // Load categories from API on mount
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const res = await fetch('/api/categories');
        const data = await res.json();
        setCategories(data);
      } catch (err) {
        console.error("Failed to load categories.json database:", err);
      }
    };
    loadCategories();
  }, []);

  // Sorted main category keys
  const sortedMainCategories = useMemo(() => {
    const source = Object.keys(categories).length > 0 ? categories : CATEGORY_MAP;
    return Object.keys(source).sort(
      (a, b) => (CATEGORY_WEIGHTS[b] || 0) - (CATEGORY_WEIGHTS[a] || 0)
    );
  }, [categories]);

  // Sorted sub category keys for current main
  const sortedSubCategories = useMemo(() => {
    const source = Object.keys(categories).length > 0 ? categories : CATEGORY_MAP;
    return getSortedSubCategories(source, mainCategory);
  }, [mainCategory, categories]);

  const setMainCategory = useCallback((nextMainCategory) => {
    setMainCategoryState((prevMainCategory) => {
      const resolvedMainCategory = typeof nextMainCategory === 'function'
        ? nextMainCategory(prevMainCategory)
        : nextMainCategory;
      const source = Object.keys(categories).length > 0 ? categories : CATEGORY_MAP;
      const nextSubCategories = getSortedSubCategories(source, resolvedMainCategory);
      if (nextSubCategories.length > 0) {
        setSubCategory(nextSubCategories[0]);
      }
      return resolvedMainCategory;
    });
  }, [categories]);

  return {
    categories,
    mainCategory, setMainCategory,
    subCategory, setSubCategory,
    currentCategory: subCategory,
    sortedMainCategories,
    sortedSubCategories,
  };
}
