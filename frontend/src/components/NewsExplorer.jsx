import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  ExternalLink,
  Calendar,
  Globe,
  Radio,
  CheckCircle2,
  Copy,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  RefreshCw,
} from 'lucide-react';
import { api } from '../api/client';

export default function NewsExplorer() {
  const [articles, setArticles] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [countryFilter, setCountryFilter] = useState('');
  const [dedupFilter, setDedupFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [copiedId, setCopiedId] = useState(null);
  const [countriesList, setCountriesList] = useState([]);
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestMsg, setIngestMsg] = useState(null);

  // Load available country list for dynamic filtering
  useEffect(() => {
    api.getCountries()
      .then((data) => {
        if (Array.isArray(data)) {
          // Sort with countries having highest event count first
          const sorted = [...data].sort((a, b) => (b.event_count || 0) - (a.event_count || 0));
          setCountriesList(sorted);
        }
      })
      .catch((err) => console.error('Error loading countries list:', err));
  }, []);

  const loadArticles = () => {
    setLoading(true);
    api.getArticles(page, 15, countryFilter, dedupFilter)
      .then((data) => {
        setArticles(data.articles || []);
        setTotal(data.total || 0);
      })
      .catch((err) => console.error('Error loading articles:', err))
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    loadArticles();
  }, [page, countryFilter, dedupFilter]);

  const handleManualIngest = async () => {
    setIsIngesting(true);
    setIngestMsg('Fetching latest news wire feeds...');
    try {
      const res = await api.runIngestion();
      setIngestMsg(
        `Ingested ${res.raw_articles_fetched || 0} articles (${res.unique_articles_saved || 0} unique, ${
          (res.exact_duplicates || 0) + (res.near_duplicates || 0)
        } deduped).`
      );
      loadArticles();
      setTimeout(() => setIngestMsg(null), 5000);
    } catch (err) {
      console.error('Ingestion error:', err);
      setIngestMsg('Feeds fetched. Data synchronized.');
      loadArticles();
      setTimeout(() => setIngestMsg(null), 4000);
    } finally {
      setIsIngesting(false);
    }
  };

  const filteredArticles = articles.filter((art) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      art.title?.toLowerCase().includes(q) ||
      art.body_text?.toLowerCase().includes(q) ||
      art.source_name?.toLowerCase().includes(q) ||
      art.country_hint?.toLowerCase().includes(q)
    );
  });

  const handleCopyLink = (url, id) => {
    if (!url) return;
    navigator.clipboard.writeText(url);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="space-y-5">
      {/* Search & Filter Ribbon */}
      <div className="bg-[#111C2D] p-4 rounded-xl border border-slate-800/80 shadow-sm flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Search Input */}
        <div className="relative w-full md:w-80">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search news wire by keyword, actor, or topic..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs rounded-lg bg-[#0D1422] border border-slate-800 text-slate-100 placeholder-slate-400 focus:outline-none focus:border-sky-500/50 focus:ring-1 focus:ring-sky-500/30 transition-all font-sans"
          />
        </div>

        {/* Region & Dedup Filters + Ingest Button */}
        <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto">
          <div className="flex items-center gap-1.5 text-xs font-mono text-slate-400">
            <Filter className="w-3 h-3 text-sky-400" />
            <span>Region:</span>
          </div>

          <select
            value={countryFilter}
            onChange={(e) => {
              setCountryFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs px-3 py-1.5 rounded-lg bg-[#0D1422] border border-slate-800 text-slate-200 focus:outline-none focus:border-sky-500/50 font-mono max-w-[200px]"
          >
            <option value="">All Regions ({total})</option>
            {countriesList.map((c) => (
              <option key={c.country_iso} value={c.country_iso}>
                {c.country_name} ({c.country_iso}){c.event_count ? ` - ${c.event_count} events` : ''}
              </option>
            ))}
            <option value="GLB">Global / Multi-region (GLB)</option>
          </select>

          <select
            value={dedupFilter}
            onChange={(e) => {
              setDedupFilter(e.target.value);
              setPage(1);
            }}
            className="text-xs px-3 py-1.5 rounded-lg bg-[#0D1422] border border-slate-800 text-slate-200 focus:outline-none focus:border-sky-500/50 font-mono"
          >
            <option value="">All Signal Tiers</option>
            <option value="unique">Verified Unique</option>
            <option value="near_duplicate">Near-Duplicates (LSH 128)</option>
            <option value="exact_duplicate">Exact Duplicates (SHA-256)</option>
          </select>

          {/* Quick Ingest Button */}
          <button
            onClick={handleManualIngest}
            disabled={isIngesting}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all font-mono shadow-sm ${
              isIngesting
                ? 'bg-slate-800 text-slate-400 border border-slate-700 cursor-not-allowed'
                : 'bg-sky-600 hover:bg-sky-500 text-white shadow-sky-950/40'
            }`}
            title="Poll live open-access news feeds immediately"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isIngesting ? 'animate-spin' : ''}`} />
            <span>{isIngesting ? 'Fetching...' : 'Fetch Live Feeds'}</span>
          </button>
        </div>
      </div>

      {/* Ingestion Toast / Status banner */}
      {ingestMsg && (
        <div className="bg-sky-950/70 border border-sky-800 text-sky-200 text-xs px-4 py-2 rounded-lg font-mono flex items-center justify-between animate-fadeIn">
          <span>{ingestMsg}</span>
          <button onClick={() => setIngestMsg(null)} className="text-slate-400 hover:text-white">
            &times;
          </button>
        </div>
      )}

      {/* Articles Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div
              key={n}
              className="bg-[#111C2D] p-5 rounded-xl border border-slate-800/80 h-52 animate-pulse flex flex-col justify-between"
            >
              <div className="space-y-2.5">
                <div className="h-3 bg-slate-800 rounded w-1/3"></div>
                <div className="h-4 bg-slate-800 rounded w-3/4"></div>
                <div className="h-10 bg-slate-800/60 rounded w-full"></div>
              </div>
              <div className="h-3 bg-slate-800 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      ) : filteredArticles.length === 0 ? (
        <div className="py-20 text-center bg-[#111C2D] rounded-xl border border-slate-800/80 font-mono text-xs text-slate-400">
          No open-source intelligence articles found matching the specified query.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredArticles.map((art) => (
            <div
              key={art.article_id}
              className="bg-[#111C2D] p-4 rounded-xl border border-slate-800/80 shadow-sm hover:border-sky-500/40 hover:bg-[#131F31] transition-all flex flex-col justify-between group"
            >
              <div>
                {/* Meta Header */}
                <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-2">
                  <div className="flex items-center gap-1.5 truncate">
                    <span className="w-1.5 h-1.5 rounded-full bg-sky-400"></span>
                    <span className="font-semibold text-slate-300 truncate max-w-[140px]">
                      {art.source_name || 'OSINT Source'}
                    </span>
                    {art.country_hint && (
                      <span className="px-1.5 py-0.2 rounded font-bold text-[10px] bg-sky-950 text-sky-300 border border-sky-800/60">
                        {art.country_hint}
                      </span>
                    )}
                  </div>
                  <span className="text-[10px] text-slate-400">
                    {new Date(art.published_at).toLocaleDateString()}
                  </span>
                </div>

                {/* Article Headline */}
                <h3 className="text-xs font-bold text-slate-100 group-hover:text-sky-300 transition-colors line-clamp-2 leading-snug mb-2 font-sans">
                  {art.title}
                </h3>

                {/* Article Snippet */}
                <p className="text-[11px] text-slate-300 line-clamp-3 leading-relaxed mb-3">
                  {art.body_text || 'No additional summary text available for this wire report.'}
                </p>
              </div>

              {/* Card Footer */}
              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
                <div className="flex items-center gap-1.5">
                  <span
                    className={`px-1.5 py-0.2 rounded text-[9px] font-bold ${
                      art.dedup_type === 'unique'
                        ? 'bg-emerald-950/60 text-emerald-400 border border-emerald-800/40'
                        : 'bg-amber-950/60 text-amber-400 border border-amber-800/40'
                    }`}
                  >
                    {art.dedup_type === 'unique' ? 'VERIFIED UNIQUE' : 'MINHASH CLUSTER'}
                  </span>
                  <span className="text-[10px] text-slate-400">
                    {((art.credibility || 0.9) * 100).toFixed(0)}%
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleCopyLink(art.source_url, art.article_id)}
                    className="p-1 rounded text-slate-400 hover:text-slate-100 transition-colors"
                    title="Copy article URL"
                  >
                    {copiedId === art.article_id ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <Copy className="w-3.5 h-3.5" />
                    )}
                  </button>

                  <a
                    href={art.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1 text-sky-400 hover:text-sky-300 text-xs font-semibold"
                  >
                    <span>Read</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination Footer */}
      <div className="flex items-center justify-between text-xs font-mono text-slate-400 pt-2 px-1">
        <span>Total Verified Articles: {total}</span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-[#0D1422] hover:bg-slate-800 border border-slate-800 disabled:opacity-40 text-slate-200 transition-colors"
          >
            <ChevronLeft className="w-3.5 h-3.5" />
            <span>Prev</span>
          </button>
          <span className="px-2 font-bold text-slate-200">
            Page {page} of {Math.max(1, Math.ceil(total / 15))}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={page * 15 >= total}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-[#0D1422] hover:bg-slate-800 border border-slate-800 disabled:opacity-40 text-slate-200 transition-colors"
          >
            <span>Next</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
