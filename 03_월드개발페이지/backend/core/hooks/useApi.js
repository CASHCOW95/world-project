import { useState, useCallback } from 'react';
import { fetchJson } from '../utils/apiClient';

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
      const data = await fetchJson('/api/history');
      setHistory(data);
    } catch (err) {
      console.error("Failed to fetch history:", err);
      setHistory([]);
    }
  }, []);

  const fetchDashboardStats = useCallback(async () => {
    try {
      const data = await fetchJson('/api/dashboard-stats');
      setDashboardStats(data);
    } catch (err) {
      console.error("Failed to fetch dashboard stats:", err);
    }
  }, []);

  const fetchPostsList = useCallback(async () => {
    try {
      const data = await fetchJson('/api/published-posts');
      setPostsList(data);
    } catch (err) {
      console.error("Failed to fetch posts list:", err);
      setPostsList([]);
    }
  }, []);

  const fetchLinksList = useCallback(async () => {
    try {
      const data = await fetchJson('/api/internal-links');
      setLinksList(data);
    } catch (err) {
      console.error("Failed to fetch links list:", err);
      setLinksList([]);
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
