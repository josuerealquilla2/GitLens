import { Component, Input, Output, EventEmitter, OnInit, OnDestroy, OnChanges, SimpleChanges, signal, ViewChild, ElementRef, AfterViewChecked, effect, untracked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { HttpHeaders } from '@angular/common/http';
import { ChatService } from '../../../../../core/services/chat/chat.service';
import { AuthCookieService } from '../../../../../core/services/cookies/authcookies.service';
import { environment } from '../../../../../../environments/environments';

export interface LangOption { code: string; label: string; flag: string; }

const LANGS: LangOption[] = [
  { code: 'es', label: 'Español',    flag: '🇪🇸' },
  { code: 'en', label: 'English',    flag: '🇬🇧' },
  { code: 'ca', label: 'Català',     flag: '🏴󠁥󠁳󠁣󠁴󠁿' },
  { code: 'fr', label: 'Français',   flag: '🇫🇷' },
  { code: 'de', label: 'Deutsch',    flag: '🇩🇪' },
  { code: 'pt', label: 'Português',  flag: '🇧🇷' },
];

@Component({
  selector: 'app-chat-room',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat-room.html',
  styleUrl: './chat-room.scss',
})
export class ChatRoom implements OnInit, OnChanges, OnDestroy, AfterViewChecked {
  @Input()  room: any = null;
  @Output() back = new EventEmitter<void>();
  @ViewChild('msgList') msgList!: ElementRef;

  texto = '';
  cargando       = signal(true);
  confirmClear   = signal(false);
  private shouldScroll = false;

  // Traducción
  readonly langs = LANGS;
  targetLang    = signal<string | null>(null);
  translatedCache = signal<Map<string, string>>(new Map());
  langMenuOpen  = signal(false);
  // Evita duplicar peticiones HTTP en vuelo para el mismo mensaje+idioma
  private pendingTranslations = new Set<string>();

  constructor(public chat: ChatService, private http: HttpClient, private cookies: AuthCookieService) {
    // Scroll automático + traducción automática de mensajes nuevos
    effect(() => {
      const msgs = this.chat.messages();
      const lang = this.targetLang();
      if (msgs.length > 0) this.shouldScroll = true;

      if (lang) {
        // untracked: leer translatedCache sin suscribir el effect a sus cambios
        // (evita el bucle: traducción completa → effect → más traducciones → ...)
        untracked(() => {
          const cache = this.translatedCache();
          msgs.forEach(m => {
            const key = `${m.id}:${lang}`;
            if (!cache.has(key) && !this.pendingTranslations.has(key)) {
              this.doTranslate(m, lang);
            }
          });
        });
      }
    });
  }

  ngOnInit() {
    if (this.room) this.loadRoom();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['room'] && !changes['room'].firstChange && this.room) {
      this.loadRoom();
    }
  }

  private loadRoom() {
    this.chat.disconnect();
    this.chat.messages.set([]);
    this.translatedCache.set(new Map());
    this.pendingTranslations.clear();
    this.targetLang.set(null);
    this.cargando.set(true);

    this.chat.getMessages(this.room.id).subscribe({
      next: (msgs) => {
        this.chat.messages.set(msgs);
        this.shouldScroll = true;
        this.cargando.set(false);
        this.chat.connectRoom(this.room.id);
      },
      error: () => {
        this.cargando.set(false);
        this.chat.connectRoom(this.room.id);
      },
    });
  }

  ngAfterViewChecked() {
    if (this.shouldScroll) { this.scrollBottom(); this.shouldScroll = false; }
  }

  ngOnDestroy() { this.chat.disconnect(); }

  enviar() {
    const txt = this.texto.trim();
    if (!txt) return;
    if (this.chat.sendMessage(txt)) { this.texto = ''; this.shouldScroll = true; }
  }

  onKey(e: KeyboardEvent) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this.enviar(); } }

  private scrollBottom() {
    const el = this.msgList?.nativeElement;
    if (el) el.scrollTop = el.scrollHeight;
  }

  myId() { return this.chat.getCurrentUserId(); }

  deleteMsg(msgId: number) {
    if (!this.room) return;
    this.chat.deleteMessage(this.room.id, msgId).subscribe({
      next: () => this.chat.messages.update(prev => prev.filter(m => m.id !== msgId)),
    });
  }

  vaciarChat() {
    if (!this.room) return;
    this.chat.clearChat(this.room.id).subscribe({
      next: () => { this.chat.messages.set([]); this.confirmClear.set(false); },
    });
  }

  formatTime(ts: string): string {
    return new Date(ts).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
  }

  formatDate(ts: string): string {
    const d = new Date(ts);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    if (d.toDateString() === today.toDateString()) return 'Hoy';
    if (d.toDateString() === yesterday.toDateString()) return 'Ayer';
    return d.toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' });
  }

  showDateSep(msgs: any[], i: number): boolean {
    if (i === 0) return true;
    return new Date(msgs[i].timestamp).toDateString() !== new Date(msgs[i - 1].timestamp).toDateString();
  }

  iniciales(nombre: string, apellidos: string): string {
    return `${nombre?.[0] ?? ''}${apellidos?.[0] ?? ''}`.toUpperCase() || '?';
  }

  // ── Traducción ──────────────────────────────────────────────

  toggleLangMenu(e: Event) { e.stopPropagation(); this.langMenuOpen.update(v => !v); }
  closeLangMenu() { this.langMenuOpen.set(false); }

  selectLang(code: string | null) {
    this.pendingTranslations.clear();
    this.translatedCache.set(new Map());
    this.targetLang.set(code);   // el effect arranca las traducciones
    this.langMenuOpen.set(false);
  }

  currentLangLabel(): string {
    if (!this.targetLang()) return 'Traducir';
    return this.langs.find(l => l.code === this.targetLang())?.flag ?? 'Traducir';
  }

  currentLangFlag(): string {
    return this.langs.find(l => l.code === this.targetLang())?.flag ?? '';
  }

  private setCache(key: string, value: string) {
    this.pendingTranslations.delete(key);
    this.translatedCache.update(prev => { const n = new Map(prev); n.set(key, value); return n; });
  }

  private doTranslate(m: any, lang: string) {
    const key = `${m.id}:${lang}`;
    this.pendingTranslations.add(key);

    if (lang === 'es') { this.setCache(key, m.content); return; }

    // Proxy Django para evitar CORS con MyMemory
    const url = `${environment.apiURL}chat/translate/?q=${encodeURIComponent(m.content)}&lang=${lang}`;
    const headers = new HttpHeaders({ Authorization: `Bearer ${this.cookies.get('gitlens_token')}` });
    this.http.get<{ translation: string }>(url, { headers }).subscribe({
      next: (res) => {
        const t    = res?.translation?.trim() ?? '';
        const orig = m.content.trim().toLowerCase();
        const isReal = t.length > 0 && t.toLowerCase() !== orig;
        this.setCache(key, isReal ? res.translation : m.content);
      },
      error: () => this.setCache(key, m.content),
    });
  }

  // Getter puro: solo lee el cache, sin efectos secundarios
  getTranslation(m: any): string | null {
    const lang = this.targetLang();
    if (!lang) return null;
    const cached = this.translatedCache().get(`${m.id}:${lang}`);
    if (!cached) return null;
    return cached.trim().toLowerCase() !== m.content.trim().toLowerCase() ? cached : null;
  }
}
