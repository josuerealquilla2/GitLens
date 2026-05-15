import { Component, OnDestroy, output, signal } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../core/services/usuario/auth.service';
import { AlertServices } from '../../../core/services/utils/alert.services';
import { Router } from '@angular/router';
import { AuthCookieService } from '../../../core/services/cookies/authcookies.service';

const MAX_INTENTOS  = 4;   // intentos antes del bloqueo
const COOLDOWN_SEG  = 30;  // segundos de bloqueo

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './login.html',
  styleUrls: ['./login.scss'],
})
export class Login implements OnDestroy {
  fnToggleLoginHeader = output();
  formLogin: FormGroup;

  errorMsg        = signal('');
  cargando        = signal(false);
  showPassword    = signal(false);
  shakeError      = signal(false);

  // Rate limiting
  intentosFallidos = signal(0);
  cooldownRestante = signal(0);
  private cooldownTimer?: ReturnType<typeof setInterval>;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private alertasService: AlertServices,
    private router: Router,
    private authCookieService: AuthCookieService
  ) {
    this.formLogin = this.fb.group({
      email:    ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
    });
  }

  get bloqueado(): boolean {
    return this.cooldownRestante() > 0;
  }

  get intentosRestantes(): number {
    return MAX_INTENTOS - this.intentosFallidos();
  }

  togglePassword() {
    this.showPassword.update(v => !v);
  }

  iniciarSesion() {
    if (this.bloqueado) return;

    if (this.formLogin.invalid) {
      this.formLogin.markAllAsTouched();
      this.triggerShake();
      return;
    }

    this.errorMsg.set('');
    this.cargando.set(true);

    this.authService.login(this.formLogin.value).subscribe({
      next: (resp) => {
        this.cargando.set(false);
        this.intentosFallidos.set(0);
        const user = resp.data;

        this.authCookieService.set('gitlens_token', user.token);
        localStorage.setItem('user', JSON.stringify(user));

        this.fnToggleLoginHeader.emit();
        this.router.navigate(['/privado']).then(() => {
          this.alertasService.alert('¡Bienvenido!', `Hola de nuevo, ${user.nombre} 👋`, 'success');
        });
      },
      error: (err) => {
        this.cargando.set(false);
        this.intentosFallidos.update(n => n + 1);
        this.triggerShake();

        // Establecer mensaje de error
        const errores = err?.error;
        let msg = 'Credenciales incorrectas.';
        if (Array.isArray(errores?.non_field_errors)) {
          msg = errores.non_field_errors[0];
        } else if (typeof errores === 'object') {
          const vals = Object.values(errores).flat() as string[];
          msg = vals[0] ?? msg;
        }
        this.errorMsg.set(msg);

        // Activar cooldown si se superó el límite
        if (this.intentosFallidos() >= MAX_INTENTOS) {
          this.iniciarCooldown();
        }
      },
    });
  }

  private iniciarCooldown() {
    this.cooldownRestante.set(COOLDOWN_SEG);
    this.errorMsg.set('');
    this.cooldownTimer = setInterval(() => {
      this.cooldownRestante.update(n => {
        if (n <= 1) {
          clearInterval(this.cooldownTimer);
          this.intentosFallidos.set(0);
          return 0;
        }
        return n - 1;
      });
    }, 1000);
  }

  private triggerShake() {
    this.shakeError.set(true);
    setTimeout(() => this.shakeError.set(false), 500);
  }

  ngOnDestroy() {
    clearInterval(this.cooldownTimer);
  }
}
