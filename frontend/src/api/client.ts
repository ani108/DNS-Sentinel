import type {
  StatsSummary,
  HourlyStat,
  TopBlockedDomain,
  DNSQuery,
  BlocklistEntry,
  WhitelistEntry,
  DomainAnalyzeResult,
  TunnelIncident
} from '../types';

const BASE_URL = 'http://localhost:8000';

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export const getStatsSummary = () => fetchAPI<StatsSummary>('/api/v1/stats/summary');
export const getHourlyStats = () => fetchAPI<HourlyStat[]>('/api/v1/stats/hourly');
export const getTopBlocked = (limit = 10) => fetchAPI<TopBlockedDomain[]>(`/api/v1/stats/top-blocked?limit=${limit}`);
export const getRecentQueries = (params?: Record<string, any>) => {
  const qs = params ? '?' + new URLSearchParams(params).toString() : '';
  return fetchAPI<DNSQuery[]>(`/api/v1/queries/recent${qs}`);
};
export const getBlocklist = () => fetchAPI<BlocklistEntry[]>('/api/v1/blocklist');
export const addToBlocklist = (domains: string[], reason: string) => fetchAPI<any>('/api/v1/blocklist', {
  method: 'POST',
  body: JSON.stringify({ domains, reason })
});
export const deleteFromBlocklist = (id: number) => fetchAPI<any>(`/api/v1/blocklist/${id}`, { method: 'DELETE' });

export const getWhitelist = () => fetchAPI<WhitelistEntry[]>('/api/v1/whitelist');
export const addToWhitelist = (domains: string[], reason: string) => fetchAPI<any>('/api/v1/whitelist', {
  method: 'POST',
  body: JSON.stringify({ domains, reason })
});
export const deleteFromWhitelist = (id: number) => fetchAPI<any>(`/api/v1/whitelist/${id}`, { method: 'DELETE' });

export const analyzeDomain = (domain: string) => fetchAPI<DomainAnalyzeResult>('/api/v1/analyze', {
  method: 'POST',
  body: JSON.stringify({ domain })
});

export const getTunnelIncidents = (status?: string) => {
  const qs = status ? `?status=${status}` : '';
  return fetchAPI<TunnelIncident[]>(`/api/v1/tunneling/incidents${qs}`);
};
export const updateTunnelIncident = (id: number, status: string) => fetchAPI<any>(`/api/v1/tunneling/incidents/${id}`, {
  method: 'PATCH',
  body: JSON.stringify({ status })
});

export const getSettings = () => fetchAPI<any>('/api/v1/settings');
export const updateSettings = (data: any) => fetchAPI<any>('/api/v1/settings', {
  method: 'PATCH',
  body: JSON.stringify(data)
});
