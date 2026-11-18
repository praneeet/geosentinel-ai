const API_BASE =
  import.meta.env.VITE_API_URL ||
  (typeof window !== "undefined" && window.location.origin
    ? `${window.location.origin}/api`
    : "http://localhost:8000/api");

export async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.detail || `Request failed with status ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  getHealth: () => apiRequest("/health"),
  getCountries: () => apiRequest("/countries"),
  getCountryRisk: (iso) => apiRequest(`/countries/${iso}/risk`),
  getCountryForecast: (iso, days = 7) => apiRequest(`/countries/${iso}/forecast?days=${days}`),
  getCountryHistory: (iso, days = 30) => apiRequest(`/countries/${iso}/history?days=${days}`),
  getCountrySummary: (iso) => apiRequest(`/countries/${iso}/summary`),
  getCountryEvents: (iso, limit = 15) => apiRequest(`/countries/${iso}/events?limit=${limit}`),
  getRiskMap: () => apiRequest("/risk/map"),
  getTrends: (days = 30) => apiRequest(`/trends?days=${days}`),
  getArticles: (page = 1, pageSize = 15, countryIso = "", dedupType = "") => {
    let query = `?page=${page}&page_size=${pageSize}`;
    if (countryIso) query += `&country_iso=${countryIso}`;
    if (dedupType) query += `&dedup_type=${dedupType}`;
    return apiRequest(`/articles${query}`);
  },
  getEvents: (page = 1, pageSize = 15, countryIso = "", category = "") => {
    let query = `?page=${page}&page_size=${pageSize}`;
    if (countryIso) query += `&country_iso=${countryIso}`;
    if (category) query += `&category=${category}`;
    return apiRequest(`/events${query}`);
  },
  getAlerts: (limit = 20) => apiRequest(`/alerts?limit=${limit}`),
  getWebhookStatus: () => apiRequest("/alerts/webhooks/status"),
  runIngestion: () => apiRequest("/ingestion/run", { method: "POST" }),
  getRiskGeoJSON: () => apiRequest("/risk/export/geojson"),
  getEventsCSVUrl: (countryIso = "") =>
    `${API_BASE}/events/export/csv${countryIso ? `?country_iso=${countryIso}` : ""}`,
};
