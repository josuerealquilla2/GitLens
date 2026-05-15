import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SocialService } from '../../../../core/services/social/social.service';
import { RepoCardComponent } from '../../../../shared/repo-card/repo-card';

@Component({
  selector: 'app-seccion-guardados',
  standalone: true,
  imports: [CommonModule, RepoCardComponent],
  templateUrl: './seccion-guardados.html',
  styleUrl: './seccion-colecciones.scss',
})
export class SeccionGuardados implements OnInit {
  repos = signal<any[]>([]);
  loading = signal(true);

  constructor(private social: SocialService) {}

  ngOnInit() {
    this.social.getGuardados().subscribe({
      next: (data) => { this.repos.set(data); this.loading.set(false); },
      error: () => this.loading.set(false),
    });
  }
}
