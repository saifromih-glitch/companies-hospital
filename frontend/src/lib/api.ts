const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://companies-hospital-production.up.railway.app";

interface FetchOptions extends RequestInit {
  token?: string;
}

export async function apiFetch<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { token, ...fetchOptions } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  
  // Merge any existing headers from options
  if (options.headers) {
    const h = options.headers;
    if (h instanceof Headers) {
      h.forEach((v, k) => { headers[k] = v; });
    } else if (Array.isArray(h)) {
      h.forEach(([k, v]) => { headers[k] = v; });
    } else {
      Object.assign(headers, h);
    }
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "خطأ في الخادم" }));
    throw new Error(error.detail || "حدث خطأ");
  }

  return response.json();
}

export interface Case {
  id: string;
  title: string;
  description: string;
  category: string;
  severity: "critical" | "high" | "medium" | "low";
  status: string;
  created_at: string;
  triage_result: {
    keywords: string[];
    suggested_experts: string[];
  };
}

export interface DashboardStats {
  total_cases: number;
  active_cases: number;
  total_companies: number;
  cases_by_severity: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
}

export async function getDashboardStats(token: string): Promise<DashboardStats> {
  return apiFetch<DashboardStats>("/api/v1/dashboard/stats", { token });
}

export async function getRecentCases(token: string): Promise<Case[]> {
  return apiFetch<Case[]>("/api/v1/cases?limit=5&sort=created_at:desc", {
    token,
  });
}
