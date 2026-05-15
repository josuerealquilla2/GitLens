import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environments';

@Injectable({
  providedIn: 'root',
})
export class RepositoriosServiceService {

  private apiUrl = environment.apiURL; // 🔥 nombre correcto

  constructor(private http: HttpClient) {}

  getRepos(filters: any): Observable<any[]> {

    let params = new HttpParams();

    if (filters.q) {
      params = params.set('q', filters.q);
    }

    if (filters.language) {
      params = params.set('language', filters.language);
    }

    if (filters.stars) {
      params = params.set('stars', filters.stars);
    }

    if (filters.page) {
      params = params.set('page', filters.page);
    }

    return this.http.get<any[]>(this.apiUrl, { params });
  }
}
