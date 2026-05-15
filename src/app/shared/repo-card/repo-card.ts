import { Component, Input, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { catchError, of } from 'rxjs';
import { SocialService } from '../../core/services/social/social.service';
import { AuthCookieService } from '../../core/services/cookies/authcookies.service';
import { LanguageIconPipe } from '../language-icon.pipe';
import { CommentsSectionComponent } from '../comments-section/comments-section';

// Dominios de badges/iconos pequeños que no queremos mostrar como preview
const BADGE_DOMAINS = ['shields.io', 'badge.fury.io', 'travis-ci', 'circleci',
  'codecov.io', 'coveralls.io', 'snyk.io', 'david-dm.org', 'npmjs.com/badge',
  'img.shields', 'badgen.net', 'hits.seeyoufarm', 'visitcount'];

const IMG_EXT = /\.(png|jpe?g|gif|webp|svg|bmp)(\?[^)\s"']*)?$/i;

@Component({
  selector: 'app-repo-card',
  standalone: true,
  imports: [CommonModule, RouterLink, LanguageIconPipe, CommentsSectionComponent],
  templateUrl: './repo-card.html',
  styleUrl: './repo-card.scss',
})
export class RepoCardComponent implements OnInit {
  @Input() repo: any;
  @Input() isAuthenticated = false;

  likeCount      = signal(0);
  liked          = signal(false);
  likeAnimating  = signal(false);
  isFavorited    = signal(false);
  isSaved        = signal(false);
  showComments   = signal(false);
  carouselIdx    = signal(0);
  readmeImages   = signal<string[]>([]);
  failedUrls     = new Set<string>();

  constructor(
    private social: SocialService,
    private cookies: AuthCookieService,
    private http: HttpClient,
  ) {}

  ngOnInit() {
    if (this.repo?.id) {
      this.social.getLikes(String(this.repo.id)).subscribe({
        next: (d) => { this.likeCount.set(d.count); this.liked.set(d.liked); }
      });
      if (this.isAuthenticated) {
        this.social.getFavoritoCheck(String(this.repo.id)).subscribe({
          next: (d) => this.isFavorited.set(d.favorito)
        });
        this.social.getGuardadoCheck(String(this.repo.id)).subscribe({
          next: (d) => this.isSaved.set(d.guardado)
        });
      }
    }
    this.fetchReadmeImages();
  }

  // ── README image extraction ────────────────────────────────

  private ownerRepo(): { owner: string; repo: string } | null {
    const url = this.repo?.url ?? this.repo?.urlRepos ?? '';
    const m = url.match(/github\.com\/([^/]+)\/([^/\s?#]+)/);
    return m ? { owner: m[1], repo: m[2].replace(/\.git$/, '') } : null;
  }

  private fetchReadmeImages() {
    const info = this.ownerRepo();
    if (!info) return;

    const { owner, repo } = info;
    // Intentamos HEAD primero, luego main, luego master si falla
    const readmeUrl = `https://raw.githubusercontent.com/${owner}/${repo}/HEAD/README.md`;

    this.http.get(readmeUrl, { responseType: 'text' }).pipe(
      catchError(() =>
        this.http.get(
          `https://raw.githubusercontent.com/${owner}/${repo}/main/README.md`,
          { responseType: 'text' }
        ).pipe(catchError(() => of('')))
      )
    ).subscribe(content => {
      if (!content) return;
      const imgs = this.parseImages(content, owner, repo);
      if (imgs.length) this.readmeImages.set(imgs);
    });
  }

  private parseImages(markdown: string, owner: string, repo: string): string[] {
    const seen = new Set<string>();
    const results: string[] = [];

    const add = (raw: string) => {
      const url = raw.trim().split(/\s+/)[0]; // quita parámetros title opcionales
      if (!url || seen.has(url)) return;
      if (!IMG_EXT.test(url)) return;
      if (BADGE_DOMAINS.some(d => url.includes(d))) return;

      seen.add(url);

      // URL absoluta: usarla tal cual
      if (/^https?:\/\//i.test(url)) {
        results.push(url);
        return;
      }

      // URL relativa → raw.githubusercontent.com
      const clean = url.replace(/^\.\//, '').replace(/^\//, '');
      results.push(`https://raw.githubusercontent.com/${owner}/${repo}/HEAD/${clean}`);
    };

    // Markdown: ![alt](url) y ![alt](url "title")
    for (const m of markdown.matchAll(/!\[[^\]]*\]\(([^)]+)\)/g)) add(m[1]);

    // HTML: <img src="..." />
    for (const m of markdown.matchAll(/<img[^>]+src=["']([^"']+)["']/gi)) add(m[1]);

    return results.slice(0, 12); // máximo 12 imágenes
  }

  // ── Carousel ──────────────────────────────────────────────

  get githubOgUrl(): string {
    const m = this.ownerRepo();
    return m ? `https://opengraph.githubassets.com/1/${m.owner}/${m.repo}` : '';
  }

  /** Prioridad: project_images → README imgs → og-image de GitHub */
  get previewImages(): string[] {
    if (this.repo?.project_images?.length > 0) return this.repo.project_images;
    const readme = this.readmeImages().filter(u => !this.failedUrls.has(u));
    if (readme.length) return readme;
    const og = this.githubOgUrl;
    return og ? [og] : [];
  }

  prevSlide(e: Event) {
    e.stopPropagation();
    const len = this.previewImages.length;
    this.carouselIdx.update(i => (i === 0 ? len - 1 : i - 1));
  }

  nextSlide(e: Event) {
    e.stopPropagation();
    const len = this.previewImages.length;
    this.carouselIdx.update(i => (i + 1) % len);
  }

  goToSlide(e: Event, idx: number) {
    e.stopPropagation();
    this.carouselIdx.set(idx);
  }

  /** Cuando una imagen del README falla, la descarta y ajusta el índice */
  onSlideImgError(url: string) {
    this.failedUrls.add(url);
    const remaining = this.previewImages.length;
    if (this.carouselIdx() >= remaining && remaining > 0) {
      this.carouselIdx.set(remaining - 1);
    }
    // Forzar re-evaluación del getter
    this.readmeImages.update(imgs => [...imgs]);
  }

  // ── Likes / Comentarios ───────────────────────────────────

  toggleLike(event: Event) {
    event.stopPropagation();
    if (!this.isAuthenticated) return;
    this.likeAnimating.set(true);
    setTimeout(() => this.likeAnimating.set(false), 400);
    this.social.toggleLike(String(this.repo.id)).subscribe({
      next: (d) => { this.likeCount.set(d.count); this.liked.set(d.liked); }
    });
  }

  toggleFav(event: Event) {
    event.stopPropagation();
    if (!this.isAuthenticated) return;
    this.social.toggleFavorito(this.repo).subscribe({
      next: (d) => this.isFavorited.set(d.favorito)
    });
  }

  toggleSave(event: Event) {
    event.stopPropagation();
    if (!this.isAuthenticated) return;
    this.social.toggleGuardado(this.repo).subscribe({
      next: (d) => this.isSaved.set(d.guardado)
    });
  }

  onVerEnGithub() {
    if (this.isAuthenticated) {
      this.social.registrarVista(this.repo).subscribe();
    }
  }

  toggleComments(event: Event) {
    event.stopPropagation();
    this.showComments.update(v => !v);
  }

  get repoId(): string { return String(this.repo?.id ?? this.repo?.name ?? ''); }
  get langKey(): string { return this.repo?.language ?? this.repo?.lenguaje ?? ''; }
}
