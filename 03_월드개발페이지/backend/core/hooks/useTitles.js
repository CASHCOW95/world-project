import { useState, useMemo, useCallback } from 'react';

/**
 * 제목 생성, 필터링, 선택, 즐겨찾기 상태 관리 hook.
 */
export default function useTitles() {
  const [titles, setTitles] = useState([]);
  const [titlesLoading, setTitlesLoading] = useState(false);
  const [selectedTitle, setSelectedTitle] = useState(null);
  const [titleFilter, setTitleFilter] = useState('전체');
  const [showAllTitles, setShowAllTitles] = useState(false);
  const [favoriteTitles, setFavoriteTitles] = useState([]);
  const [customTitle, setCustomTitle] = useState('');

  const handleGenerateTitles = useCallback(async (kwObj, catName) => {
    if (!kwObj) return;
    setTitlesLoading(true);
    setTitles([]);
    setSelectedTitle(null);
    setCustomTitle('');
    try {
      const res = await fetch('/api/generate-titles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: kwObj.keyword,
          category: catName,
        }),
      });
      const data = await res.json();
      if (data && Array.isArray(data)) {
        const scored = data
          .map((t) => {
            const ctr = parseFloat((8.5 + ((t.title.length % 7) * 0.2)).toFixed(1));
            const seo = 75 + (t.title.length % 5) * 5;
            const score = ctr * 10 + seo;
            return { ...t, ctr, seo, score };
          })
          .sort((a, b) => b.score - a.score);

        setTitles(scored);
        if (scored.length > 0) {
          setSelectedTitle(scored[0]);
          setCustomTitle(scored[0].title);
        }
      }
    } catch (err) {
      console.error("Failed to generate titles:", err);
    } finally {
      setTitlesLoading(false);
    }
  }, []);

  const filteredTitles = useMemo(() => {
    if (titleFilter === '전체') return titles;
    return titles.filter(t => t.type === titleFilter);
  }, [titles, titleFilter]);

  const toggleFavoriteTitle = useCallback((tObj, e) => {
    if (e) e.stopPropagation();
    setFavoriteTitles(prev =>
      prev.some(item => item.title === tObj.title)
        ? prev.filter(item => item.title !== tObj.title)
        : [...prev, tObj]
    );
  }, []);

  const selectTitle = useCallback((t) => {
    setSelectedTitle(t);
    setCustomTitle(t.title);
  }, []);

  const resetTitles = useCallback(() => {
    setTitles([]);
    setSelectedTitle(null);
    setCustomTitle('');
  }, []);

  return {
    titles,
    titlesLoading,
    selectedTitle, setSelectedTitle,
    titleFilter, setTitleFilter,
    showAllTitles, setShowAllTitles,
    favoriteTitles,
    customTitle, setCustomTitle,
    handleGenerateTitles,
    filteredTitles,
    toggleFavoriteTitle,
    selectTitle,
    resetTitles,
  };
}
