import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environments';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class CategoriaLenguajeServiceService {

  private URL = environment.apiURL+'repositorios/';
  //private apiUrl = 'http://127.0.0.1:8000/api/repositorios/';

  // 🔥 estado compartido
  private lenguajeSubject = new BehaviorSubject<string>('');
  lenguaje$ = this.lenguajeSubject.asObservable();

  private busquedaSubject = new BehaviorSubject<string>('');
  busqueda$ = this.busquedaSubject.asObservable();

  constructor(private http: HttpClient) {}

  resetear() {
    this.lenguajeSubject.next('');
    this.busquedaSubject.next('');
  }

  cambiarLenguaje(lenguaje: string) {
    this.busquedaSubject.next('');
    this.lenguajeSubject.next(lenguaje);
  }

  buscarTexto(query: string) {
    this.lenguajeSubject.next('');
    this.busquedaSubject.next(query);
  }

  getRepos(lenguaje: string, page: number = 1) {
    return this.http.get(`${this.URL}?lenguaje=${lenguaje}&page=${page}`);
  }

  buscarRepos(query: string, page: number = 1) {
    return this.http.get(`${this.URL}?q=${encodeURIComponent(query)}&page=${page}`);
  }
}
