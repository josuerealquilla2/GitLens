import { Component, output } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../../core/services/usuario/auth.service';
import { AlertServices } from '../../../core/services/utils/alert.services';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrls: ['./login.scss'],
})
export class Login {
  fnToggleLoginHeader = output();
  formLogin: FormGroup;

  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private alertasService: AlertServices,
    private router: Router
  ) {
    this.formLogin = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
    });
  }

  iniciarSesion() {
    if (this.formLogin.invalid) {
      this.alertasService.alert('Error', 'Formulario no válido', 'error');
      return;
    }

    const datos = {
      email: this.formLogin.value.email,
      password: this.formLogin.value.password,
    };

    this.alertasService.showLoader('Iniciando sesión...');
    this.authService.login(datos).subscribe({
      next: (resp) => {
        this.alertasService.hide();
        sessionStorage.setItem('token', resp.data.token);
        sessionStorage.setItem('user', JSON.stringify(resp.data));
        this.alertasService.alert('Bienvenido', `Hola ${resp.data.nombre}`, 'success');
        this.fnToggleLoginHeader.emit();
        this.router.navigate(['/app']);
      },
      error: (err) => {
        this.alertasService.hide();
        this.alertasService.popupErrores(err);
      },
    });
  }
}
