import { Component, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject, combineLatest, of } from 'rxjs';
import { debounceTime, switchMap, tap, catchError, takeUntil } from 'rxjs/operators';
import { CategoriaLenguajeServiceService } from '../../../../core/services/categoria_lenguaje_Services/categoria-lenguaje-service.service';
import { SocialService } from '../../../../core/services/social/social.service';
import { AuthCookieService } from '../../../../core/services/cookies/authcookies.service';
import { RepoCardComponent } from '../../../../shared/repo-card/repo-card';

@Component({
  selector: 'app-repositorios-por-lenguaje',
  standalone: true,
  imports: [CommonModule, RepoCardComponent],
  templateUrl: './repositorios-por-lenguaje.html',
  styleUrl: './repositorios-por-lenguaje.scss',
})
export class RepositoriosPorLenguaje implements OnInit, OnDestroy {
  repos: any[] = [];
  loading       = signal(false);
  page          = 1;
  lenguajeActual = '';
  busquedaActual = '';
  modo: 'popular' | 'lenguaje' | 'busqueda' = 'popular';
  isAuthenticated = false;

  private destroy$ = new Subject<void>();

  constructor(
    private reposService: CategoriaLenguajeServiceService,
    private social: SocialService,
    private cookies: AuthCookieService
  ) {}

  ngOnInit() {
    this.isAuthenticated = !!this.cookies.get('gitlens_token');

    combineLatest([this.reposService.lenguaje$, this.reposService.busqueda$]).pipe(
      // Colapsa las dos emisiones síncronas de BehaviorSubject en una sola
      debounceTime(0),
      // Limpia inmediatamente y activa skeleton antes de la petición
      tap(([lenguaje, busqueda]) => {
        this.repos          = [];
        this.page           = 1;
        this.lenguajeActual = lenguaje;
        this.busquedaActual = busqueda;
        this.modo = busqueda ? 'busqueda' : lenguaje ? 'lenguaje' : 'popular';
        this.loading.set(true);
      }),
      // Cancela la petición anterior si llega una nueva antes de que termine
      switchMap(([lenguaje, busqueda]) => {
        const obs = busqueda
          ? this.reposService.buscarRepos(busqueda, 1)
          : lenguaje
            ? this.reposService.getRepos(lenguaje, 1)
            : this.social.getReposPopulares(1);

        return obs.pipe(catchError(() => of({ repos: [] })));
      }),
      takeUntil(this.destroy$)
    ).subscribe({
      next: (data: any) => {
        this.repos = data.repos ?? [];
        this.loading.set(false);
      }
    });
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }

  // Paginación: petición directa (no pasa por el stream de filtros)
  cargar() {
    this.loading.set(true);
    this.repos = [];

    const obs = this.modo === 'busqueda'
      ? this.reposService.buscarRepos(this.busquedaActual, this.page)
      : this.modo === 'lenguaje'
        ? this.reposService.getRepos(this.lenguajeActual, this.page)
        : this.social.getReposPopulares(this.page);

    obs.pipe(takeUntil(this.destroy$)).subscribe({
      next: (data: any) => { this.repos = data.repos ?? []; this.loading.set(false); },
      error: ()          => this.loading.set(false),
    });
  }

  siguiente() { this.page++; this.cargar(); }
  anterior()  { if (this.page > 1) { this.page--; this.cargar(); } }
}
