import { Injectable, signal } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environments';
import { AuthCookieService } from '../cookies/authcookies.service';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private base = environment.apiURL + 'chat/';

  rooms        = signal<any[]>([]);
  messages     = signal<any[]>([]);
  activeRoomId = signal<number | null>(null);
  connected    = signal(false);

  private currentRoomId: number | null = null;
  private pollTimer: ReturnType<typeof setInterval> | null = null;

  constructor(private http: HttpClient, private cookies: AuthCookieService) {}

  private h(): HttpHeaders {
    return new HttpHeaders({ Authorization: `Bearer ${this.cookies.get('gitlens_token')}` });
  }

  getRooms(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}rooms/`, { headers: this.h() });
  }

  getGlobalRoom(): Observable<any> {
    return this.http.get<any>(`${this.base}rooms/global/`, { headers: this.h() });
  }

  createRoom(data: { room_type: string; member_ids: number[]; name?: string }): Observable<any> {
    return this.http.post<any>(`${this.base}rooms/`, data, { headers: this.h() });
  }

  getMessages(roomId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}rooms/${roomId}/messages/`, { headers: this.h() });
  }

  /** Abre sala: carga historial via REST y empieza polling cada 2 s */
  connectRoom(roomId: number) {
    this.disconnect();
    this.currentRoomId = roomId;
    this.activeRoomId.set(roomId);
    this.connected.set(true);
    this._startPolling(roomId);
  }

  private _startPolling(roomId: number) {
    this.pollTimer = setInterval(() => {
      if (this.currentRoomId !== roomId) return;
      this.getMessages(roomId).subscribe({
        next: (msgs) => {
          if (this.currentRoomId !== roomId) return;
          const knownIds = new Set(this.messages().map(m => m.id));
          const nuevos = msgs.filter(m => !knownIds.has(m.id));
          if (nuevos.length > 0) this.messages.update(prev => [...prev, ...nuevos]);
        }
      });
    }, 2000);
  }

  /** Envía mensaje vía REST y lo añade al listado al recibir confirmación del servidor */
  sendMessage(content: string): boolean {
    if (!this.connected() || this.currentRoomId === null) return false;
    const roomId = this.currentRoomId;

    this.http.post<any>(
      `${this.base}rooms/${roomId}/messages/`,
      { content },
      { headers: this.h() }
    ).subscribe({
      next: (msg) => {
        this.messages.update(prev => {
          if (prev.some(m => m.id === msg.id)) return prev;
          return [...prev, {
            id:               msg.id,
            content:          msg.content,
            sender_id:        msg.sender_id,
            sender_nombre:    msg.sender_nombre,
            sender_apellidos: msg.sender_apellidos,
            timestamp:        msg.timestamp,
          }];
        });
      }
    });

    return true;
  }

  deleteRoom(roomId: number): Observable<void> {
    return this.http.delete<void>(`${this.base}rooms/${roomId}/`, { headers: this.h() });
  }

  deleteMessage(roomId: number, msgId: number): Observable<void> {
    return this.http.delete<void>(`${this.base}rooms/${roomId}/messages/${msgId}/`, { headers: this.h() });
  }

  clearChat(roomId: number): Observable<void> {
    return this.http.delete<void>(`${this.base}rooms/${roomId}/clear/`, { headers: this.h() });
  }

  disconnect() {
    this.currentRoomId = null;
    if (this.pollTimer) { clearInterval(this.pollTimer); this.pollTimer = null; }
    this.connected.set(false);
  }

  getCurrentUserId(): number {
    try {
      return JSON.parse(localStorage.getItem('user') ?? '{}').id ?? 0;
    } catch { return 0; }
  }
}
