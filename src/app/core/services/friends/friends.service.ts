import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../../environments/environments';
import { AuthCookieService } from '../cookies/authcookies.service';

@Injectable({ providedIn: 'root' })
export class FriendsService {
  private base  = environment.apiURL + 'friends/';
  private users = environment.apiURL + 'users/';

  constructor(private http: HttpClient, private cookies: AuthCookieService) {}

  private h(): HttpHeaders {
    return new HttpHeaders({ Authorization: `Bearer ${this.cookies.get('gitlens_token')}` });
  }

  searchUsers(q: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}search/?q=${encodeURIComponent(q)}`, { headers: this.h() });
  }

  sendRequest(receiverId: number): Observable<any> {
    return this.http.post(`${this.base}requests/`, { receiver_id: receiverId }, { headers: this.h() });
  }

  getPendingRequests(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}requests/`, { headers: this.h() });
  }

  respondRequest(id: number, action: 'accept' | 'reject'): Observable<any> {
    return this.http.patch(`${this.base}requests/${id}/`, { action }, { headers: this.h() });
  }

  getFriends(): Observable<any[]> {
    return this.http.get<any[]>(`${this.base}`, { headers: this.h() });
  }

  removeFriend(friendshipId: number): Observable<void> {
    return this.http.delete<void>(`${this.base}${friendshipId}/`, { headers: this.h() });
  }

  getFriendCount(): Observable<{ friend_count: number; pending_requests: number }> {
    return this.http.get<any>(`${this.base}count/`, { headers: this.h() });
  }

  getUserStatus(userId: number): Observable<any> {
    return this.http.get<any>(`${this.base}status/${userId}/`, { headers: this.h() });
  }
}
