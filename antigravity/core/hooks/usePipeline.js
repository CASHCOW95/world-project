import { useState, useRef, useEffect, useCallback } from 'react';

const MAX_LOGS = 500;

/**
 * SSE 스트리밍 파이프라인 실행 hook.
 * Single 모드와 Cluster 모드를 모두 지원.
 * AbortController로 강제 중지 가능.
 * 로그 배열 상한(500줄)으로 메모리 누수 방지.
 */
export default function usePipeline() {
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [terminalStep, setTerminalStep] = useState('');
  const [copied, setCopied] = useState(false);

  // Cluster-specific progress state
  const [clusterCurrent, setClusterCurrent] = useState(0);
  const [clusterStatusLabel, setClusterStatusLabel] = useState('대기 중...');

  const terminalEndRef = useRef(null);
  const abortControllerRef = useRef(null);

  // Auto-scroll terminal
  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const addLog = useCallback((logText) => {
    setLogs(prev => {
      const next = [...prev, logText];
      return next.length > MAX_LOGS ? next.slice(-MAX_LOGS) : next;
    });
  }, []);

  const parseSingleStepLog = useCallback((logText) => {
    if (logText.includes('[STEP-1]')) setTerminalStep('역분석');
    else if (logText.includes('[STEP-2]')) setTerminalStep('글생성');
    else if (logText.includes('[STEP-3]')) setTerminalStep('이미지생성');
    else if (logText.includes('[STEP-4]') || logText.includes('[STEP-5]')) setTerminalStep('평가');
    else if (logText.includes('[STEP-6]') || logText.includes('[STEP-9]')) setTerminalStep('발행');
  }, []);

  const parseClusterStepLog = useCallback((logText, clusterTotal) => {
    if (logText.includes('[CLUSTER-1]')) {
      setTerminalStep('역분석');
      setClusterCurrent(0);
      setClusterStatusLabel('토픽 클러스터 구조 생성 중...');
    } else if (logText.includes('[CLUSTER-2]')) {
      setClusterStatusLabel('RAG 기반 자료 수집 및 정보 분석 중...');
    } else if (logText.includes('[CLUSTER-3-')) {
      setTerminalStep('글생성');
      const match = logText.match(/\[CLUSTER-3-(\d+)\]/);
      if (match && match[1]) {
        const postIdx = parseInt(match[1]);
        setClusterCurrent(postIdx);
        if (postIdx === 1) {
          setClusterStatusLabel('메인 종합 가이드 포스트 생성 중...');
        } else {
          setClusterStatusLabel(`서브글 ${postIdx - 1}/${clusterTotal - 1} 생성 및 분석 중...`);
        }
      }
    } else if (logText.includes('[CLUSTER-4]')) {
      setTerminalStep('발행');
      setClusterStatusLabel(`서브글 ${clusterTotal - 1}/${clusterTotal - 1} 메인글 내부링크 연결 중`);
    } else if (logText.includes('[CLUSTER-5]')) {
      setTerminalStep('완료');
      setClusterCurrent(clusterTotal);
      setClusterStatusLabel('클러스터 전체 발행 및 텔레그램 리포트 완료');
    }
  }, []);

  /**
   * SSE 스트림을 읽고 파싱하는 공통 함수.
   * @param {Response} response - fetch Response 객체
   * @param {'single' | 'cluster'} mode - 파이프라인 모드
   * @param {number} clusterTotal - 클러스터 모드일 때 총 글 수
   * @param {Function} onComplete - 완료 시 콜백 (예: fetchHistory)
   */
  const processSSEStream = useCallback(async (response, mode, clusterTotal, onComplete) => {
    if (!response.body) {
      throw new Error("서버 스트리밍이 차단되었습니다.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop();

        lines.forEach(line => {
          if (line.startsWith('data: ')) {
            try {
              const payload = JSON.parse(line.replace('data: ', ''));

              if (payload.log) {
                addLog(payload.log);
                if (mode === 'cluster') {
                  parseClusterStepLog(payload.log, clusterTotal);
                } else {
                  parseSingleStepLog(payload.log);
                }
              }

              if (payload.success && payload.result) {
                setResult(payload.result);
                setTerminalStep('완료');
                if (onComplete) onComplete();
              }

              if (payload.error) {
                setError(payload.error);
                setTerminalStep('에러');
              }
            } catch (e) {
              console.error("Streaming JSON parse error:", e);
            }
          }
        });
      }
    } finally {
      reader.releaseLock();
    }
  }, [addLog, parseSingleStepLog, parseClusterStepLog]);

  /**
   * 단일 글 파이프라인 실행.
   */
  const runSinglePipeline = useCallback(async (payload, onComplete) => {
    setPipelineRunning(true);
    setError('');
    setResult(null);
    setLogs([]);
    setTerminalStep('역분석');

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('/api/publish-pipeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: abortControllerRef.current.signal,
      });
      await processSSEStream(response, 'single', 0, onComplete);
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message);
        setTerminalStep('에러');
      }
    } finally {
      setPipelineRunning(false);
      abortControllerRef.current = null;
    }
  }, [processSSEStream]);

  /**
   * 클러스터 파이프라인 실행.
   */
  const runClusterPipeline = useCallback(async (payload, clusterTotal, onComplete) => {
    setPipelineRunning(true);
    setError('');
    setResult(null);
    setLogs([]);
    setTerminalStep('역분석');
    setClusterCurrent(0);
    setClusterStatusLabel('대기 중...');

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('/api/cluster-publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: abortControllerRef.current.signal,
      });
      await processSSEStream(response, 'cluster', clusterTotal, onComplete);
    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message);
        setTerminalStep('에러');
      }
    } finally {
      setPipelineRunning(false);
      abortControllerRef.current = null;
    }
  }, [processSSEStream]);

  const abortPipeline = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setTerminalStep('중지');
      setPipelineRunning(false);
    }
  }, []);

  const handleCopy = useCallback((html) => {
    if (!html) return;
    navigator.clipboard.writeText(html);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, []);

  return {
    pipelineRunning,
    logs,
    result, setResult,
    error,
    terminalStep,
    copied,
    clusterCurrent,
    clusterStatusLabel,
    terminalEndRef,
    runSinglePipeline,
    runClusterPipeline,
    abortPipeline,
    handleCopy,
  };
}
