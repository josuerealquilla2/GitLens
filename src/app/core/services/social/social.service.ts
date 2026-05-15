import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environments';
import { AuthCookieService } from '../cookies/authcookies.service';

@Injectable({ providedIn: 'root' })
export class SocialService {
  private base = environment.apiURL + 'repos/';

  constructor(private http: HttpClient, private cookies: AuthCookieService) {}

  private authHeaders(): HttpHeaders {
    const token = this.cookies.get('gitlens_token');
    return new HttpHeaders({ Authorization: `Bearer ${token}` });
  }

  // ── Likes ──
  getLikes(repoId: string): Observable<{ count: number; liked: boolean }> {
    return this.http.get<any>(`${this.base}${repoId}/likes/`, { headers: this.authHeaders() });
  }
  toggleLike(repoId: string): Observable<{ liked: boolean; count: number }> {
    return this.http.post<any>(`${this.base}${repoId}/like/`, {}, { headers: this.authHeaders() });
  }

  // ── Comentarios ──
  getComments(repoId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}${repoId}/comments/`);
  }
  postComment(repoId: string, body: string, parentId?: number): Observable<any> {
    const payload: any = { body };
    if (parentId) payload['parent'] = parentId;
    return this.http.post<any>(`${this.base}${repoId}/comments/`, payload, { headers: this.authHeaders() });
  }
  deleteComment(commentId: number): Observable<void> {
    return this.http.delete<void>(`${this.base}comments/${commentId}/`, { headers: this.authHeaders() });
  }

  // ── Favoritos ──
  getFavoritos(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}favoritos/`, { headers: this.authHeaders() });
  }
  toggleFavorito(repo: any): Observable<any> {
    return this.http.post<any>(`${this.base}favoritos/`, this._repoPayload(repo), { headers: this.authHeaders() });
  }
  getFavoritoCheck(repoId: string): Observable<{ favorito: boolean }> {
    return this.http.get<{ favorito: boolean }>(`${this.base}favoritos/${repoId}/check/`, { headers: this.authHeaders() });
  }

  // ── Guardados ──
  getGuardados(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}guardados/`, { headers: this.authHeaders() });
  }
  toggleGuardado(repo: any): Observable<any> {
    return this.http.post<any>(`${this.base}guardados/`, this._repoPayload(repo), { headers: this.authHeaders() });
  }
  getGuardadoCheck(repoId: string): Observable<{ guardado: boolean }> {
    return this.http.get<{ guardado: boolean }>(`${this.base}guardados/${repoId}/check/`, { headers: this.authHeaders() });
  }

  // ── Historial ──
  getHistorial(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}historial/`, { headers: this.authHeaders() });
  }
  registrarVista(repo: any): Observable<any> {
    return this.http.post<any>(`${this.base}historial/`, this._repoPayload(repo), { headers: this.authHeaders() });
  }

  // ── Públicos ──
  getReposPopulares(page = 1): Observable<any> {
    return this.http.get<any>(`${this.base}populares/?page=${page}`);
  }
  getReposTendencias(lenguaje = '', page = 1): Observable<any> {
    return this.http.get<any>(`${this.base}tendencias/?lenguaje=${lenguaje}&page=${page}`);
  }

  private _repoPayload(repo: any) {
    return {
      github_id: repo.id,
      name: repo.name,
      owner: repo.owner ?? repo.creador ?? '',
      owner_avatar: repo.owner_avatar ?? repo.avatar ?? '',
      description: repo.description ?? repo.about ?? '',
      language: repo.language ?? repo.lenguaje ?? '',
      stars: repo.stars ?? repo.numerodeEstrellas ?? 0,
      url: repo.url ?? repo.urlRepos ?? '',
    };
  }
}
