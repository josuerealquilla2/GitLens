import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from '../../../../environments/environments';

@Injectable({
  providedIn: 'root',
})
export class ReposSinRegistroService{
  private URL=environment.apiURL

  constructor(private http:HttpClient) {
  }
  getReposSinRegistro():Observable<any>{
    return this.http.get<any>(`${this.URL}/repositorios/populares/`)
  }

}
