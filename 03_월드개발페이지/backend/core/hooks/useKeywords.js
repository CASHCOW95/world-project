import { useState, useEffect, useMemo, useCallback } from 'react';

/**
 * 키워드 fetch, 정렬, 필터링, 선택 상태 관리 hook.
 * useMemo로 정렬 결과를 캐싱하여 불필요한 재계산을 방지.
 */
export default function useKeywords({ onKeywordSelected } = {}) {
  const [keywordLoading, setKeywordLoading] = useState(false);
  const [keywords, setKeywords] = useState([]);
  const [selectedKeyword, setSelectedKeyword] = useState(null);
  const [keywordSearch, setKeywordSearch] = useState('');
  const [keywordSortType, setKeywordSortType] = useState('recommend');
  const [showAllKeywords, setShowAllKeywords] = useState(false);

  const fetchKeywords = useCallback(async (catName) => {
    setKeywordLoading(true);
    try {
      const res = await fetch(`/api/keywords?category=${encodeURIComponent(catName)}`);
      const data = await res.json();
      setKeywords(data);
      if (data.length > 0) {
        setSelectedKeyword(data[0]);
        if (onKeywordSelected) onKeywordSelected(data[0], catName);
      }
    } catch (err) {
      console.error("Failed to fetch keywords:", err);
    } finally {
      setKeywordLoading(false);
    }
  }, [onKeywordSelected]);

  // Memoized sorted + filtered keywords
  const filteredKeywords = useMemo(() => {
    let sorted = [...keywords];
    if (keywordSortType === 'volume') {
      sorted.sort((a, b) => b.search_volume - a.search_volume);
    } else if (keywordSortType === 'cpc') {
      sorted.sort((a, b) => b.cpc_dollar - a.cpc_dollar);
    } else if (keywordSortType === 'latest') {
      sorted.sort((a, b) => a.keyword.localeCompare(b.keyword));
    } else {
      sorted.sort((a, b) => b.golden_score - a.golden_score || b.search_volume - a.search_volume);
    }
    if (keywordSearch) {
      sorted = sorted.filter(kw =>
        kw.keyword.toLowerCase().includes(keywordSearch.toLowerCase())
      );
    }
    return sorted;
  }, [keywords, keywordSortType, keywordSearch]);

  const visibleKeywords = useMemo(() => {
    return showAllKeywords ? filteredKeywords : filteredKeywords.slice(0, 10);
  }, [filteredKeywords, showAllKeywords]);

  const resetKeywords = useCallback(() => {
    setSelectedKeyword(null);
    setKeywords([]);
    setShowAllKeywords(false);
  }, []);

  return {
    keywordLoading,
    keywords,
    selectedKeyword, setSelectedKeyword,
    keywordSearch, setKeywordSearch,
    keywordSortType, setKeywordSortType,
    showAllKeywords, setShowAllKeywords,
    fetchKeywords,
    filteredKeywords,
    visibleKeywords,
    resetKeywords,
  };
}
