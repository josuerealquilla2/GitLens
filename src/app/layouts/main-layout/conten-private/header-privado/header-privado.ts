import { Component, HostListener, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthCookieService } from '../../../../core/services/cookies/authcookies.service';
import { Router } from '@angular/router';
import { CategoriaLenguajeServiceService } from '../../../../core/services/categoria_lenguaje_Services/categoria-lenguaje-service.service';
import { NavigationService, NavSection } from '../../../../core/services/navigation/navigation.service';
import { ThemeService } from '../../../../core/services/theme/theme.service';

@Component({
  selector: 'app-header-privado',
  imports: [CommonModule, FormsModule],
  templateUrl: './header-privado.html',
  styleUrl: './header-privado.scss',
  standalone: true,
})
export class HeaderPrivado {
  theme = inject(ThemeService);
  sidebarOpen = signal<boolean>(false);
  abierto = false;
  searchQuery = '';

  private user = (() => {
    try { return JSON.parse(localStorage.getItem('user') ?? '{}'); }
    catch { return {}; }
  })();

  iniciales(): string {
    const n = this.user?.nombre ?? '';
    const a = this.user?.apellidos ?? '';
    return `${n[0] ?? ''}${a[0] ?? ''}`.toUpperCase() || '?';
  }

  constructor(
    private authCookieService: AuthCookieService,
    private router: Router,
    private lenguajeService: CategoriaLenguajeServiceService,
    public navService: NavigationService
  ) {}

  toggleDropdown() { this.abierto = !this.abierto; }

  @HostListener('document:click')
  cerrarDropdown() { this.abierto = false; }

  navigate(section: NavSection) {
    if (section === 'inicio') this.lenguajeService.resetear();
    this.navService.navigate(section);
    this.abierto = false;
  }

  seleccionarLenguaje(lenguaje: string) {
    this.abierto = false;
    this.lenguajeService.cambiarLenguaje(lenguaje); // primero el valor
    this.navService.navigate('inicio');              // luego el componente monta con el valor correcto
  }

  buscar() {
    const q = this.searchQuery.trim();
    if (!q) return;
    this.lenguajeService.buscarTexto(q);
    this.navService.navigate('inicio');
  }

  onSearchKey(event: KeyboardEvent) {
    if (event.key === 'Enter') this.buscar();
  }

  toggleSidebar() { this.sidebarOpen.update(v => !v); }

  logout() {
    this.authCookieService.delete('gitlens_token');
    localStorage.removeItem('user');
    this.router.navigate(['/']);
  }
}
