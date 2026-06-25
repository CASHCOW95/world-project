import { useState, useEffect, useMemo } from 'react';
import { CATEGORY_MAP, CATEGORY_WEIGHTS, SUBCAT_WEIGHTS } from '../components/constants';

/**
 * 카테고리 로드 및 mainCategory ↔ subCategory 연동 로직을 관리하는 hook.
 */
export default function useCategories() {
  const [categories, setCategories] = useState({});
  const [mainCategory, setMainCategory] = useState('정부정책');
  const [subCategory, setSubCategory] = useState('정부지원금');
  const [currentCategory, setCurrentCategory] = useState('정부지원금');

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
    const subCats = categories[mainCategory]
      ? Object.keys(categories[mainCategory])
      : (CATEGORY_MAP[mainCategory] || []);
    return subCats.sort(
      (a, b) => (SUBCAT_WEIGHTS[b] || 0) - (SUBCAT_WEIGHTS[a] || 0)
    );
  }, [mainCategory, categories]);

  // Auto-select first subcategory when main changes
  useEffect(() => {
    if (sortedSubCategories.length > 0) {
      setSubCategory(sortedSubCategories[0]);
    }
  }, [sortedSubCategories]);

  // Sync currentCategory with subCategory
  useEffect(() => {
    if (subCategory) {
      setCurrentCategory(subCategory);
    }
  }, [subCategory]);

  return {
    categories,
    mainCategory, setMainCategory,
    subCategory, setSubCategory,
    currentCategory,
    sortedMainCategories,
    sortedSubCategories,
  };
}
