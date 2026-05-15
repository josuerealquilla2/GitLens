import { Component, output, signal } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../core/services/usuario/auth.service';
import { EmailValidator } from '../../../core/validators/email.validator';
import { checkPasswordValidator } from '../../../core/validators/password.validator';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './register.html',
  styleUrl: './register.scss',
})
export class Register {
  registerForm: FormGroup;
  fnToggleRegisterHeader = output();
  registroExitoso = signal(false);
  cargando = signal(false);
  errorMsg = signal('');

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
  ) {
    this.registerForm = this.formBuilder.group({
      email:     ['', [Validators.required, EmailValidator]],
      nombre:    ['', [Validators.required]],
      apellidos: ['', [Validators.required]],
      password1: ['', [Validators.required, checkPasswordValidator]],
      password2: ['', [Validators.required, checkPasswordValidator]],
    });
  }

  registrame() {
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      return;
    }

    this.errorMsg.set('');
    this.cargando.set(true);

    this.authService.registro(this.registerForm.value).subscribe({
      next: () => {
        this.cargando.set(false);
        this.registroExitoso.set(true);
        this.registerForm.reset();
      },
      error: (err) => {
        this.cargando.set(false);
        const errores = err?.error;
        if (Array.isArray(errores?.non_field_errors)) {
          this.errorMsg.set(errores.non_field_errors[0]);
        } else if (typeof errores === 'object') {
          const vals = Object.values(errores).flat() as string[];
          this.errorMsg.set(vals[0] ?? 'No se pudo crear la cuenta.');
        } else {
          this.errorMsg.set('No se pudo crear la cuenta. Inténtalo de nuevo.');
        }
      },
    });
  }
}
