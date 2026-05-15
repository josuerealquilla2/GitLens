import { Injectable, signal, effect } from '@angular/core';

export type Theme = 'dark' | 'light';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private saved = (localStorage.getItem('gitlens_theme') as Theme) ?? 'dark';
  theme = signal<Theme>(this.saved);

  constructor() {
    this.apply(this.saved);
    effect(() => {
      const t = this.theme();
      this.apply(t);
      localStorage.setItem('gitlens_theme', t);
    });
  }

  toggle() {
    this.theme.update(t => t === 'dark' ? 'light' : 'dark');
  }

  private apply(t: Theme) {
    document.documentElement.setAttribute('data-theme', t);
  }
}
