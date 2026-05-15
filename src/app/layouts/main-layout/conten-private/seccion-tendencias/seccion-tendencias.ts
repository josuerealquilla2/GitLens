import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SocialService } from '../../../../core/services/social/social.service';
import { RepoCardComponent } from '../../../../shared/repo-card/repo-card';

@Component({
  selector: 'app-seccion-tendencias',
  standalone: true,
  imports: [CommonModule, RepoCardComponent],
  templateUrl: './seccion-tendencias.html',
  styleUrl: './seccion-tendencias.scss',
})
export class SeccionTendencias implements OnInit {
  repos = signal<any[]>([]);
  loading = signal(true);
  lenguaje = '';
  page = 1;

  readonly lenguajes = ['', 'Python', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'Java', 'C++'];

  constructor(private social: SocialService) {}

  ngOnInit() { this.cargar(); }

  filtrar(lang: string) {
    this.lenguaje = lang;
    this.page = 1;
    this.cargar();
  }

  cargar(append = false) {
    this.loading.set(true);
    this.social.getReposTendencias(this.lenguaje, this.page).subscribe({
      next: (data) => {
        const nuevos = data.repos ?? [];
        this.repos.update(prev => append ? [...prev, ...nuevos] : nuevos);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  cargarMas() { this.page++; this.cargar(true); }
}
