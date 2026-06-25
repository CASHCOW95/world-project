import { useState, useCallback } from 'react';

/**
 * V2 에이전트 대시보드의 API 유틸리티 hook.
 * history, dashboardStats, postsList, linksList를 관리.
 */
export default function useApi() {
  const [history, setHistory] = useState([]);
  const [dashboardStats, setDashboardStats] = useState({
    total_published: 0,
    total_pending: 0,
    total_failed: 0,
    total_clusters: 0,
    total_links: 0,
    today_published: 0,
  });
  const [postsList, setPostsList] = useState([]);
  const [linksList, setLinksList] = useState([]);

  const fetchHistory = useCallback(async () => {
    try {
      const res = await fetch('/api/history');
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      console.error("Failed to fetch history:", err);
    }
  }, []);

  const fetchDashboardStats = useCallback(async () => {
    try {
      const res = await fetch('/api/dashboard-stats');
      const data = await res.json();
      setDashboardStats(data);
    } catch (err) {
      console.error("Failed to fetch dashboard stats:", err);
    }
  }, []);

  const fetchPostsList = useCallback(async () => {
    try {
      const res = await fetch('/api/published-posts');
      const data = await res.json();
      setPostsList(data);
    } catch (err) {
      console.error("Failed to fetch posts list:", err);
    }
  }, []);

  const fetchLinksList = useCallback(async () => {
    try {
      const res = await fetch('/api/internal-links');
      const data = await res.json();
      setLinksList(data);
    } catch (err) {
      console.error("Failed to fetch links list:", err);
    }
  }, []);

  return {
    history,
    dashboardStats,
    postsList,
    linksList,
    fetchHistory,
    fetchDashboardStats,
    fetchPostsList,
    fetchLinksList,
  };
}
