import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../../../../core/services/chat/chat.service';
import { FriendsService } from '../../../../core/services/friends/friends.service';
import { ChatRoom } from './chat-room/chat-room';

@Component({
  selector: 'app-seccion-chat',
  standalone: true,
  imports: [CommonModule, FormsModule, ChatRoom],
  templateUrl: './seccion-chat.html',
  styleUrl: './seccion-chat.scss',
})
export class SeccionChat implements OnInit {
  activeRoom = signal<any>(null);
  cargando   = signal(true);
  showChat   = signal(false);  // móvil: alterna entre lista y sala

  modalOpen  = signal(false);
  modalTipo  = signal<'privado' | 'grupo'>('privado');
  amigos     = signal<any[]>([]);
  selIds     = new Set<number>();
  grupoName  = '';

  constructor(public chat: ChatService, private friends: FriendsService) {}

  ngOnInit() {
    this.chat.getRooms().subscribe({
      next: (rooms) => { this.chat.rooms.set(rooms); this.cargando.set(false); },
      error: ()      => this.cargando.set(false),
    });
  }

  abrirRoom(room: any) { this.activeRoom.set(room); this.showChat.set(true); }

  cerrarChat() { this.activeRoom.set(null); this.showChat.set(false); }

  abrirModal(tipo: 'privado' | 'grupo') {
    this.modalTipo.set(tipo);
    this.selIds.clear();
    this.grupoName = '';
    this.modalOpen.set(true);
    this.friends.getFriends().subscribe({ next: (f) => this.amigos.set(f) });
  }

  toggleAmigo(id: number) {
    if (this.selIds.has(id)) this.selIds.delete(id);
    else {
      if (this.modalTipo() === 'privado') this.selIds.clear();
      this.selIds.add(id);
    }
  }

  crearChat() {
    const tipo  = this.modalTipo();
    const ids   = Array.from(this.selIds);
    if (!ids.length) return;
    const data: any = { room_type: tipo, member_ids: ids };
    if (tipo === 'grupo') data.name = this.grupoName || 'Grupo';

    this.chat.createRoom(data).subscribe({
      next: (room) => {
        this.chat.rooms.update(prev => {
          const exists = prev.find(r => r.id === room.id);
          return exists ? prev : [room, ...prev];
        });
        this.modalOpen.set(false);
        this.activeRoom.set(room);
      },
    });
  }

  lastMsg(room: any): string {
    const m = room.last_message;
    if (!m) return 'Sin mensajes aún';
    return m.content?.length > 40 ? m.content.slice(0, 40) + '…' : m.content;
  }

  iniciales(nombre: string, apellidos = ''): string {
    return `${nombre?.[0] ?? ''}${apellidos?.[0] ?? ''}`.toUpperCase() || '?';
  }

  roomIniciales(room: any): string {
    const n = room.display_name ?? '';
    const parts = n.split(' ');
    return `${parts[0]?.[0] ?? ''}${parts[1]?.[0] ?? ''}`.toUpperCase() || '?';
  }
}
