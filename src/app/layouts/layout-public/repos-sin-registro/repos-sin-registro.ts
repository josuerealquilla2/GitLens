import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SocialService } from '../../../core/services/social/social.service';
import { RepoCardComponent } from '../../../shared/repo-card/repo-card';
import { AuthModalService } from '../../../core/services/authModal/auth-modal.service';

@Component({
  selector: 'app-repos-sin-registro',
  templateUrl: 'repos-sin-registro.html',
  styleUrl: 'repos-sin-registro.scss',
  imports: [CommonModule, RepoCardComponent],
  standalone: true,
})
export class ReposSinRegistro implements OnInit {
  repos   = signal<any[]>([]);
  loading = signal(true);

  constructor(
    private social:    SocialService,
    private authModal: AuthModalService,
  ) {}

  ngOnInit() {
    this.cargar();
  }

  cargar() {
    this.loading.set(true);
    this.social.getReposPopulares(1).subscribe({
      next: (data) => {
        const todos: any[] = data.repos ?? [];

        // Ordenar por popularidad (estrellas) descendente
        const sorted = [...todos].sort(
          (a, b) =>
            (b.stars ?? b.numerodeEstrellas ?? 0) -
            (a.stars ?? a.numerodeEstrellas ?? 0),
        );

        // Shuffle parcial dentro del top 30% para variedad visual
        const corte = Math.max(15, Math.floor(sorted.length * 0.3));
        const top   = sorted.slice(0, corte);
        for (let i = top.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [top[i], top[j]] = [top[j], top[i]];
        }

        this.repos.set(top.slice(0, 15));
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  abrirRegistro() { this.authModal.showRegister(); }
  abrirLogin()    { this.authModal.showLogin(); }
}
