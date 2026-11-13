import { useEffect, useRef, useState } from 'react';

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

  useEffect(() => {
    let isMounted = true;

    function connect() {
      try {
        const ws = new WebSocket(WS_BASE);
        wsRef.current = ws;

        ws.onopen = () => {
          if (!isMounted) return;
          setIsConnected(true);
          console.log("[GeoSentinel WS] Connected to live alert engine.");
        };

        ws.onmessage = (event) => {
          if (!isMounted) return;
          try {
            const data = JSON.parse(event.data);
            setLatestAlert(data);
            if (onAlertReceived) {
              onAlertReceived(data);
            }
          } catch (err) {
            console.warn("[GeoSentinel WS] Non-JSON message received:", event.data);
          }
        };

        ws.onclose = () => {
          if (!isMounted) return;
          setIsConnected(false);
          console.log("[GeoSentinel WS] Connection lost. Reconnecting in 3 seconds...");
          reconnectTimeoutRef.current = setTimeout(connect, 3000);
        };

        ws.onerror = (err) => {
          console.error("[GeoSentinel WS] Socket error:", err);
          ws.close();
        };
      } catch (e) {
        if (isMounted) {
          reconnectTimeoutRef.current = setTimeout(connect, 3000);
        }
      }
    }

    connect();

    // Keepalive ping interval
    const pingInterval = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send("ping");
      }
    }, 25000);

    return () => {
      isMounted = false;
      clearInterval(pingInterval);
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  return { isConnected, latestAlert };
}
