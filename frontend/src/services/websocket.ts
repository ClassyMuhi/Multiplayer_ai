import { AppEvent } from '../types';

export type WebSocketStatus = 'CONNECTING' | 'CONNECTED' | 'DISCONNECTED' | 'ERROR';
export type EventHandler = (event: AppEvent) => void;
export type StatusHandler = (status: WebSocketStatus) => void;

export class ProjectWebSocket {
  private ws: WebSocket | null = null;
  private projectId: string;
  private userId: string;
  private userName: string;
  private eventHandlers: Set<EventHandler> = new Set();
  private statusHandlers: Set<StatusHandler> = new Set();
  private reconnectTimeout: any = null;
  private isExplicitlyClosed = false;
  private status: WebSocketStatus = 'DISCONNECTED';

  constructor(projectId: string, userId: string, userName: string) {
    this.projectId = projectId;
    this.userId = userId;
    this.userName = userName;
  }

  public connect(): void {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.isExplicitlyClosed = false;
    this.updateStatus('CONNECTING');

    // Connect directly to backend port 8000 or through proxy
    const wsHost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? '127.0.0.1:8000'
      : window.location.host;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    
    const wsUrl = `${protocol}//${wsHost}/api/projects/${encodeURIComponent(this.projectId)}/agent/stream?user_id=${encodeURIComponent(
      this.userId
    )}&user_name=${encodeURIComponent(this.userName)}`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        this.updateStatus('CONNECTED');
        if (this.reconnectTimeout) {
          clearTimeout(this.reconnectTimeout);
          this.reconnectTimeout = null;
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          this.notifyEvent(parsed as AppEvent);
        } catch (e) {
          console.warn('[WS] Failed to parse message:', event.data);
        }
      };

      this.ws.onerror = (error) => {
        console.error('[WS] Error:', error);
        this.updateStatus('ERROR');
      };

      this.ws.onclose = () => {
        this.updateStatus('DISCONNECTED');
        if (!this.isExplicitlyClosed) {
          this.scheduleReconnect();
        }
      };
    } catch (err) {
      console.error('[WS] Connection failed to initialize:', err);
      this.updateStatus('ERROR');
      this.scheduleReconnect();
    }
  }

  public disconnect(): void {
    this.isExplicitlyClosed = true;
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.updateStatus('DISCONNECTED');
  }

  public send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(typeof data === 'string' ? data : JSON.stringify(data));
    } else {
      console.warn('[WS] Cannot send message, socket not open');
    }
  }

  public onEvent(handler: EventHandler): () => void {
    this.eventHandlers.add(handler);
    return () => this.eventHandlers.delete(handler);
  }

  public onStatus(handler: StatusHandler): () => void {
    this.statusHandlers.add(handler);
    handler(this.status);
    return () => this.statusHandlers.delete(handler);
  }

  private updateStatus(newStatus: WebSocketStatus): void {
    this.status = newStatus;
    this.statusHandlers.forEach((handler) => handler(newStatus));
  }

  private notifyEvent(event: AppEvent): void {
    this.eventHandlers.forEach((handler) => handler(event));
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimeout || this.isExplicitlyClosed) return;
    this.reconnectTimeout = setTimeout(() => {
      this.reconnectTimeout = null;
      if (!this.isExplicitlyClosed) {
        this.connect();
      }
    }, 3000);
  }
}

// Singleton manager for ease of use across pages
class WebSocketService {
  private activeSocket: ProjectWebSocket | null = null;
  private eventHandlers: Set<EventHandler> = new Set();
  private connectionHandlers: Set<(connected: boolean) => void> = new Set();

  public connect(projectId: string, userId: string = 'dev-user', userName: string = 'Developer'): void {
    if (this.activeSocket) {
      this.activeSocket.disconnect();
    }

    this.activeSocket = new ProjectWebSocket(projectId, userId, userName);

    this.activeSocket.onStatus((status) => {
      const isConnected = status === 'CONNECTED';
      this.connectionHandlers.forEach((h) => h(isConnected));
    });

    this.activeSocket.onEvent((event) => {
      this.eventHandlers.forEach((h) => h(event));
    });

    this.activeSocket.connect();
  }

  public disconnect(): void {
    if (this.activeSocket) {
      this.activeSocket.disconnect();
      this.activeSocket = null;
    }
  }

  public onEvent(handler: EventHandler): () => void {
    this.eventHandlers.add(handler);
    return () => this.eventHandlers.delete(handler);
  }

  public onConnectionChange(handler: (connected: boolean) => void): () => void {
    this.connectionHandlers.add(handler);
    return () => this.connectionHandlers.delete(handler);
  }

  public send(data: any): void {
    this.activeSocket?.send(data);
  }
}

export const wsService = new WebSocketService();
