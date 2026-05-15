import { Component, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subject, debounceTime, distinctUntilChanged, switchMap, of, catchError } from 'rxjs';
import { FriendsService } from '../../../../core/services/friends/friends.service';

type Tab = 'buscar' | 'solicitudes' | 'amigos';

@Component({
  selector: 'app-seccion-amigos',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './seccion-amigos.html',
  styleUrl: './seccion-amigos.scss',
})
export class SeccionAmigos implements OnInit, OnDestroy {
  tab         = signal<Tab>('buscar');
  query       = '';
  sugerencias = signal<any[]>([]);
  resultados  = signal<any[]>([]);
  solicitudes = signal<any[]>([]);
  amigos      = signal<any[]>([]);
  buscando    = signal(false);
  cargandoSol = signal(false);
  cargandoAm  = signal(false);
  dropdownOpen = signal(false);

  sentRequests = new Set<number>();
  private dropdownTouched = false;   // evita cerrar dropdown al tocar una sugerencia

  private query$ = new Subject<string>();
  private destroy$ = new Subject<void>();

  constructor(private friends: FriendsService) {}

  ngOnInit() {
    this.cargarSolicitudes();
    this.cargarAmigos();

    this.query$.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap(q => {
        if (q.trim().length < 2) {
          this.sugerencias.set([]);
          this.dropdownOpen.set(false);
          return of([]);
        }
        this.buscando.set(true);
        return this.friends.searchUsers(q).pipe(
          catchError(() => { this.buscando.set(false); return of([]); })
        );
      }),
    ).subscribe({
      next: (data) => {
        this.sugerencias.set(data);
        this.dropdownOpen.set(data.length > 0);
        this.buscando.set(false);
      },
    });
  }

  ngOnDestroy() { this.destroy$.next(); this.destroy$.complete(); }

  onInput() {
    this.query$.next(this.query);
    if (!this.query.trim()) {
      this.dropdownOpen.set(false);
      this.sugerencias.set([]);
    }
  }

  seleccionar(u: any) {
    const yaEsta = this.resultados().some(r => r.id === u.id);
    if (!yaEsta) this.resultados.update(prev => [u, ...prev]);
    this.dropdownOpen.set(false);
    this.query = '';
    this.sugerencias.set([]);
  }

  onDropdownPointerDown() { this.dropdownTouched = true; }

  cerrarDropdown() {
    if (this.dropdownTouched) { this.dropdownTouched = false; return; }
    setTimeout(() => this.dropdownOpen.set(false), 200);
  }

  cambiarTab(t: Tab) {
    this.tab.set(t);
    this.dropdownOpen.set(false);
    if (t === 'solicitudes') this.cargarSolicitudes();
    if (t === 'amigos')     this.cargarAmigos();
  }

  enviarSolicitud(userId: number) {
    this.sentRequests.add(userId);
    this.friends.sendRequest(userId).subscribe({
      error: () => this.sentRequests.delete(userId),
    });
  }

  cargarSolicitudes() {
    this.cargandoSol.set(true);
    this.friends.getPendingRequests().subscribe({
      next: (data) => { this.solicitudes.set(data); this.cargandoSol.set(false); },
      error: ()     => this.cargandoSol.set(false),
    });
  }

  responder(id: number, action: 'accept' | 'reject') {
    this.friends.respondRequest(id, action).subscribe({
      next: () => this.solicitudes.update(prev => prev.filter(s => s.id !== id)),
    });
  }

  cargarAmigos() {
    this.cargandoAm.set(true);
    this.friends.getFriends().subscribe({
      next: (data) => { this.amigos.set(data); this.cargandoAm.set(false); },
      error: ()     => this.cargandoAm.set(false),
    });
  }

  eliminarAmigo(friendshipId: number, nombre: string) {
    if (!confirm(`¿Eliminar a ${nombre} de tus amigos?`)) return;
    this.friends.removeFriend(friendshipId).subscribe({
      next: () => this.amigos.update(prev => prev.filter(a => a.id !== friendshipId)),
    });
  }

  iniciales(nombre: string, apellidos: string): string {
    return `${nombre?.[0] ?? ''}${apellidos?.[0] ?? ''}`.toUpperCase() || '?';
  }
}
