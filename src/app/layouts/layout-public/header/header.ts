import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Login } from '../login/login';
import { Register } from '../register/register';
import { AuthModalService } from '../../../core/services/authModal/auth-modal.service';
import { ThemeService } from '../../../core/services/theme/theme.service';

@Component({
  selector: 'app-header',
  imports: [Login, Register, CommonModule],
  templateUrl: './header.html',
  styleUrl: './header.scss',
  standalone: true,
})
export class Header {
  private authModal = inject(AuthModalService);
  theme = inject(ThemeService);

  menuOpen     = signal(false);
  openLogin    = this.authModal.openLogin;
  openRegister = this.authModal.openRegister;

  toogleLogin()    { this.authModal.toggleLogin();    this.menuOpen.set(false); }
  toggleRegister() { this.authModal.toggleRegister(); this.menuOpen.set(false); }
  toggleMenu()     { this.menuOpen.update(v => !v); }
}
