import { Injectable } from '@angular/core';
import {environment} from '../../../../environments/environments';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private URL =environment.apiURL;
  constructor(private http :HttpClient){

  }

  registro(datos:any):Observable<any>{
    return this.http.post<any>(`${this.URL}/users/register/`,datos)
  }
  login(datos:any):Observable<any>{
    return this.http.post<any>(`${this.URL}/users/login/`,datos)
  }


}
