import React, { useState, useEffect } from 'react';
import { Search, Filter, ExternalLink, Calendar, Shield, Globe, Tag, Sparkles } from 'lucide-react';
import { api } from '../api/client';

export default function NewsExplorer() {
  const [articles, setArticles] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [countryFilter, setCountryFilter] = useState('');
  const [dedupFilter, setDedupFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    api.getArticles(page, 12, countryFilter, dedupFilter)
      .then((data) => {
        if (!isMounted) return;
        setArticles(data.articles || []);
        setTotal(data.total || 0);
      })
      .catch((err) => console.error("Error loading articles:", err))
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [page, countryFilter, dedupFilter]);

  const filteredArticles = articles.filter((art) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      art.title.toLowerCase().includes(q) ||
      art.body_text.toLowerCase().includes(q) ||
      art.source_name.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-4">
      {/* Search & Filter Bar */}
      <div className="glass-panel p-4 rounded-xl border border-sentinel-700/60 shadow-lg flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search global news wire by keyword..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs rounded-lg bg-sentinel-950 border border-sentinel-700 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          {/* Country Selector */}
          <select
            value={countryFilter}
            onChange={(e) => {
              setCountryFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs px-3 py-2 rounded-lg bg-sentinel-950 border border-sentinel-700 text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Regions</option>
            <option value="UKR">Ukraine (UKR)</option>
            <option value="RUS">Russia (RUS)</option>
            <option value="CHN">China (CHN)</option>
            <option value="TWN">Taiwan (TWN)</option>
            <option value="IND">India (IND)</option>
            <option value="USA">United States (USA)</option>
            <option value="ISR">Israel (ISR)</option>
            <option value="IRN">Iran (IRN)</option>
            <option value="DEU">Germany (DEU)</option>
          </select>

          {/* Deduplication Status Selector */}
          <select
            value={dedupFilter}
            onChange={(e) => {
              setDedupFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs px-3 py-2 rounded-lg bg-sentinel-950 border border-sentinel-700 text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Deduplication Types</option>
            <option value="unique">Unique Articles</option>
            <option value="near_duplicate">Near-Duplicates (MinHash LSH)</option>
            <option value="exact_duplicate">Exact Duplicates (SHA-256)</option>
          </select>
        </div>
      </div>

      {/* Articles Grid */}
      {loading ? (
        <div className="py-20 text-center text-cyan-400 font-mono text-sm animate-pulse">
          Streaming Cleaned &amp; Normalized Articles...
        </div>
      ) : filteredArticles.length === 0 ? (
        <div className="py-16 text-center text-slate-400 glass-panel rounded-xl font-mono text-xs">
          No articles found matching current criteria.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredArticles.map((art) => (
            <div
              key={art.article_id}
              className="glass-panel p-4 rounded-xl border border-sentinel-700/60 shadow-lg hover:border-cyan-500/50 transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono mb-2">
                  <span className="font-semibold text-slate-300 truncate max-w-[160px]">
                    {art.source_name}
                  </span>
                  <span>{new Date(art.published_at).toLocaleDateString()}</span>
                </div>

                <h3 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors line-clamp-2 leading-snug mb-2">
                  {art.title}
                </h3>

                <p className="text-xs text-slate-300 line-clamp-3 leading-relaxed mb-3">
                  {art.body_text}
                </p>
              </div>

              <div className="pt-3 border-t border-sentinel-800 flex items-center justify-between text-xs">
                <div className="flex items-center gap-1.5 font-mono text-[10px]">
                  <span
                    className={`px-2 py-0.5 rounded font-bold ${
                      art.dedup_type === 'unique'
                        ? 'bg-emerald-950/70 text-emerald-400 border border-emerald-800/50'
                        : 'bg-amber-950/70 text-amber-400 border border-amber-800/50'
                    }`}
                  >
                    {art.dedup_type === 'unique' ? 'UNIQUE' : 'NEAR-DUP'}
                  </span>
                  <span className="text-slate-400">
                    Cred: {(art.credibility * 100).toFixed(0)}%
                  </span>
                </div>

                <a
                  href={art.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 text-xs font-medium"
                >
                  <span>Source</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination Controls */}
      <div className="flex items-center justify-between text-xs font-mono text-slate-400 pt-2">
        <span>Total Articles: {total}</span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1 rounded bg-sentinel-900 hover:bg-sentinel-800 border border-sentinel-700 disabled:opacity-40"
          >
            Previous
          </button>
          <span className="px-2 font-bold text-white">Page {page}</span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={page * 12 >= total}
            className="px-3 py-1 rounded bg-sentinel-900 hover:bg-sentinel-800 border border-sentinel-700 disabled:opacity-40"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
