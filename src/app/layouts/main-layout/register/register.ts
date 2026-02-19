import {Component, output} from '@angular/core';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {AuthService} from '../../../core/services/usuario/auth.service';
import {AlertServices} from '../../../core/services/utils/alert.services';
import {EmailValidator} from '../../../core/validators/email.validator';
import {NgClass} from '@angular/common';
import {checkPasswordValidator} from '../../../core/validators/password.validator'


@Component({
  selector: 'app-register',
  imports: [NgClass, ReactiveFormsModule],
  templateUrl: './register.html',
  styleUrl: './register.scss',

})
export class Register {
  registerForm:FormGroup;
  fnToggleRegisterHeader=output();

constructor(
  private formBuilder:FormBuilder,
  private authService:AuthService,
  private alert:AlertServices,

) {
  this.registerForm=this.formBuilder.group({

    "email": ["",[Validators.required,EmailValidator]],
    "nombre": ["",[Validators.required]],
    "apellidos": ["",[Validators.required]],
    "password1": ["",[Validators.required,checkPasswordValidator]],
    "password2":["",[Validators.required,checkPasswordValidator]],

  })

}
  registrame(){
    if(this.registerForm.invalid){
      alert("el registro es invalido")
      return;
    }
    console.log(this.registerForm.value)
    setTimeout(() => {
      this.alert.showLoader("registrando..")
    },2000)

    this.authService.registro(this.registerForm.value).subscribe({
      next: (data) => {
        this.alert.hide()
        setTimeout(() => {
          this.alert.alert(
            "Cuenta creada correctamente",
            "Su cuenta ha sido creada correctamente. Inicie sesión para acceder a su panel de control",
            "success",
          )
        },2000)
        this.registerForm.reset();
      },
      error: (err) => {
        this.alert.hide()
        setTimeout(() => {
          this.alert.popupErrores(err)
        },2000)
        this.alert.hide()
      }
    })

  }



}
