import { useEffect, useRef, useState, useCallback } from 'react';

const WS_BASE =
  import.meta.env.VITE_WS_URL ||
  (typeof window !== "undefined" && window.location.host
    ? `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/ws/alerts`
    : "ws://localhost:8000/ws/alerts");

export function useWebSocketAlerts(onAlertReceived) {
  const [isConnected, setIsConnected] = useState(false);
  const [latestAlert, setLatestAlert] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const retryCountRef = useRef(0);
  const seenAlertIdsRef = useRef(new Set());
  const callbackRef = useRef(onAlertReceived);

  // Keep callback ref fresh without triggering reconnect effect
  useEffect(() => {
    callbackRef.current = onAlertReceived;
  }, [onAlertReceived]);

  useEffect(() => {
    let isMounted = true;

    function scheduleReconnect() {
      if (!isMounted) return;
      retryCountRef.current += 1;
      // Exponential backoff with jitter: min 1s, max 30s, +/- 20% random jitter
      const baseDelay = Math.min(30000, 1000 * Math.pow(1.5, retryCountRef.current));
      const jitter = 0.8 + Math.random() * 0.4;
      const delay = Math.round(baseDelay * jitter);

      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = setTimeout(() => {
        if (isMounted) connect();
      }, delay);
    }

    function connect() {
      try {
        if (wsRef.current && (wsRef.current.readyState === WebSocket.CONNECTING || wsRef.current.readyState === WebSocket.OPEN)) {
          return;
        }

        const ws = new WebSocket(WS_BASE);
        wsRef.current = ws;

        ws.onopen = () => {
          if (!isMounted) return;
          setIsConnected(true);
          retryCountRef.current = 0; // reset retry backoff on successful connection
          console.log("[GeoSentinel WS] Connected to live alert engine.");
        };

        ws.onmessage = (event) => {
          if (!isMounted) return;
          try {
            const data = JSON.parse(event.data);
            // Deduplicate incoming alert broadcasts
            const dedupeKey = data.alert_id || `${data.country}-${data.timestamp}`;
            if (dedupeKey && seenAlertIdsRef.current.has(dedupeKey)) {
              return;
            }
            if (dedupeKey) {
              seenAlertIdsRef.current.add(dedupeKey);
              // Cap seen set to prevent memory growth
              if (seenAlertIdsRef.current.size > 200) {
                const arr = Array.from(seenAlertIdsRef.current);
                seenAlertIdsRef.current = new Set(arr.slice(-100));
              }
            }

            setLatestAlert(data);
            if (callbackRef.current) {
              callbackRef.current(data);
            }
          } catch (err) {
            console.debug("[GeoSentinel WS] Heartbeat / non-alert message:", event.data);
          }
        };

        ws.onclose = () => {
          if (!isMounted) return;
          setIsConnected(false);
          scheduleReconnect();
        };

        ws.onerror = (err) => {
          console.warn("[GeoSentinel WS] Socket error:", err);
          try {
            ws.close();
          } catch (_) {}
        };
      } catch (e) {
        if (isMounted) {
          scheduleReconnect();
        }
      }
    }

    connect();

    // Keepalive ping interval
    const pingInterval = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        try {
          wsRef.current.send("ping");
        } catch (_) {}
      }
    }, 25000);

    return () => {
      isMounted = false;
      clearInterval(pingInterval);
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) {
        try {
          wsRef.current.close();
        } catch (_) {}
      }
    };
  }, []);

  return { isConnected, latestAlert };
}
