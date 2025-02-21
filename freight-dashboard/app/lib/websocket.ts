import { useEffect, useState } from "react";

const SOCKET_URL = "ws://localhost:8000/ws";  // ✅ Match FastAPI WebSocket

interface WebSocketMessage {
  type: string;
  payload: any;
}

export function useWebSocket() {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [freighterUpdates, setFreighterUpdates] = useState<any[]>([]);
  const [shipmentUpdates, setShipmentUpdates] = useState<any[]>([]);
  const [activeUsers, setActiveUsers] = useState<any[]>([]);

  useEffect(() => {
    const ws = new WebSocket(SOCKET_URL);

    ws.onopen = () => console.log("Connected to WebSocket");
    
    ws.onmessage = (event) => {
      const message: WebSocketMessage = JSON.parse(event.data);
      console.log("WebSocket Received:", message);

      switch (message.type) {
        case "user_login":
          setActiveUsers((prev) => [...prev, message.payload])
          break;
        case "user_logout":
          setActiveUsers((prev) => prev.filter(u => u.userid !== message.payload.userid))
          break;
        case "freighter_update":
          setFreighterUpdates((prev) => message.payload);
          break;
        case "shipment_update":
          setShipmentUpdates((prev) => message.payload);
          break;
        default:
          console.warn("Unknown WebSocket message type:", message.type);
      }
    };

    ws.onclose = () => console.log("WebSocket Disconnected");

    setSocket(ws);
    return () => ws.close();
  }, []);

  const sendMessage = (type: string, payload: any) => {
    if (socket) {
      socket.send(JSON.stringify({ type, payload }));
    }
  };

  return { activeUsers, freighterUpdates, shipmentUpdates, sendMessage };
}
