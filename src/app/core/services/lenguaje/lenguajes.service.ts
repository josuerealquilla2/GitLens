import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from '../../../../environments/environments';

@Injectable({
  providedIn: 'root',
})
export class LenguajesService{
  private URL=environment.apiURL
  constructor(private http:HttpClient)
  {}
  getLenguajes():Observable<any>{
    return this.http.get<any>(`${this.URL}/api/users/lenguajes`)
  }
}
