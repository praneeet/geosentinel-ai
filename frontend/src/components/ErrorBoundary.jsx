import React from 'react';
import { AlertOctagon, RefreshCw } from 'lucide-react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("GTOC Critical UI Error Caught by Boundary:", error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReload = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-[#06090e] text-slate-100 flex items-center justify-center p-6">
          <div className="max-w-lg w-full glass-panel p-8 rounded-2xl border border-rose-800/80 shadow-[0_0_50px_rgba(244,63,94,0.15)] text-center space-y-5">
            <div className="w-16 h-16 rounded-2xl bg-rose-950/80 border border-rose-600/70 mx-auto flex items-center justify-center text-rose-400">
              <AlertOctagon className="w-8 h-8" />
            </div>

            <div className="space-y-1">
              <h1 className="text-xl font-bold font-mono uppercase tracking-wider text-white">
                GTOC Operational Telemetry Interrupted
              </h1>
              <p className="text-xs text-slate-400 font-mono">
                An unexpected exception was isolated by the GTOC Resilience Boundary.
              </p>
            </div>

            {this.state.error && (
              <div className="p-3.5 rounded-lg bg-black/60 border border-sentinel-800 text-left font-mono text-[11px] text-rose-300 overflow-x-auto">
                {this.state.error.toString()}
              </div>
            )}

            <button
              onClick={this.handleReload}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-mono text-xs font-bold bg-cyan-600 hover:bg-cyan-500 text-white transition-all shadow-lg shadow-cyan-900/40"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Reset &amp; Re-establish Telemetry Feed</span>
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

