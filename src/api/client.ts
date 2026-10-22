export const apiConfig = {
  baseURL: '/api/v1',
  mode: 'backend' as const,
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiConfig.baseURL}${path}`, {
    ...init,
    headers: { Accept: 'application/json', ...(init?.headers || {}) },
  })
  if (!response.ok) {
    const detail = await response.text().catch(() => '')
    throw new Error(detail || `HTTP ${response.status}`)
  }
  return response.json() as Promise<T>
}

export function apiWebSocketUrl(path: string) {
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${location.host}${apiConfig.baseURL}${path}`
}
