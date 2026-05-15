import { Injectable, signal } from '@angular/core';

export type NavSection = 'inicio' | 'tendencias' | 'repositorios' | 'historial' | 'favoritos' | 'perfil' | 'amigos' | 'chat';

@Injectable({ providedIn: 'root' })
export class NavigationService {
  activeSection = signal<NavSection>('inicio');

  navigate(section: NavSection) {
    this.activeSection.set(section);
  }
}
