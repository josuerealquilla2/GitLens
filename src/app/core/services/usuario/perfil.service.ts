import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environments';
import { AuthCookieService } from '../cookies/authcookies.service';

@Injectable({ providedIn: 'root' })
export class PerfilService {
  private base = environment.apiURL + 'users/';

  constructor(private http: HttpClient, private cookies: AuthCookieService) {}

  private headers(): HttpHeaders {
    return new HttpHeaders({ Authorization: `Bearer ${this.cookies.get('gitlens_token')}` });
  }

  getMiPerfil(): Observable<any> {
    return this.http.get<any>(`${this.base}yo`, { headers: this.headers() });
  }

  actualizarPerfil(data: any): Observable<any> {
    return this.http.patch<any>(`${this.base}yo`, data, { headers: this.headers() });
  }
}
