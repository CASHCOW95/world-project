export async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json') ? await response.json() : null;

  if (!response.ok) {
    const message = data?.error || data?.message || `HTTP ${response.status}`;
    throw new Error(message);
  }

  return data;
}

export function getErrorMessage(error, fallback = '요청 처리 중 오류가 발생했습니다.') {
  return error instanceof Error && error.message ? error.message : fallback;
}
