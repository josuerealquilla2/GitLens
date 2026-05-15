import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class AuthModalService {
  openLogin    = signal(false);
  openRegister = signal(false);

  showLogin()      { this.openLogin.set(true);  this.openRegister.set(false); }
  showRegister()   { this.openRegister.set(true); this.openLogin.set(false); }
  toggleLogin()    { this.openLogin.update(v => !v); this.openRegister.set(false); }
  toggleRegister() { this.openRegister.update(v => !v); this.openLogin.set(false); }
}
