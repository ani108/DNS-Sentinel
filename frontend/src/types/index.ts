export interface DNSQuery {
  id: number;
  queried_at: string;
  domain: string;
  query_type: string;
  client_ip: string;
  verdict: 'ALLOWED' | 'BLOCKED' | 'SINKHOLED';
  block_reason?: string;
  ml_score?: number;
  is_tunneling: boolean;
  response_time_ms: number;
}

export interface StatsSummary {
  total_queries: number;
  blocked_queries: number;
  allowed_queries: number;
  tunneling_detected: number;
  active_feeds: number;
  blocklist_size: number;
}

export interface HourlyStat {
  hour: string;
  allowed: number;
  blocked: number;
  tunneling: number;
}

export interface TopBlockedDomain {
  domain: string;
  count: number;
}

export interface BlocklistEntry {
  id: number;
  domain: string;
  added_by: string;
  reason: string;
  created_at: string;
}

export interface WhitelistEntry {
  id: number;
  domain: string;
  added_by: string;
  reason: string;
  created_at: string;
}

export interface DomainAnalyzeResult {
  domain: string;
  verdict: 'CLEAN' | 'BLOCKED' | 'SUSPICIOUS';
  ml_score: number;
  features: Record<string, any>;
  threat_intel_match: boolean;
  threat_intel_source?: string;
  threat_category?: string;
  explanation: string;
}

export interface TunnelIncident {
  id: number;
  base_domain: string;
  client_ip: string;
  unique_subdomains: number;
  avg_entropy: number;
  avg_subdomain_length: number;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'ACTIVE' | 'RESOLVED' | 'FALSE_POSITIVE';
  detected_at: string;
  resolved_at?: string;
}
