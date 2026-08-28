import { useState, useEffect, useRef } from 'react';
import type { DNSQuery } from '../types';

export function useTrafficStream(url: string = 'ws://localhost:8000/ws/traffic') {
  const [queries, setQueries] = useState<DNSQuery[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    let reconnectTimeout: ReturnType<typeof setTimeout>;
    let pingInterval: ReturnType<typeof setInterval>;

    const connect = () => {
      ws.current = new WebSocket(url);

      ws.current.onopen = () => {
        setIsConnected(true);
        pingInterval = setInterval(() => {
          if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);
      };

      ws.current.onmessage = (event) => {
        try {
          const newQuery: DNSQuery = JSON.parse(event.data);
          setQueries((prev) => [newQuery, ...prev].slice(0, 50));
        } catch (e) {
          console.error('WebSocket parsing error:', e);
        }
      };

      ws.current.onclose = () => {
        setIsConnected(false);
        clearInterval(pingInterval);
        reconnectTimeout = setTimeout(connect, 5000);
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        ws.current?.close();
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimeout);
      clearInterval(pingInterval);
      ws.current?.close();
    };
  }, [url]);

  return { queries, isConnected };
}
