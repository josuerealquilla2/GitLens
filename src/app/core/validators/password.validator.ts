import {AbstractControl, ValidationErrors} from '@angular/forms';


export function checkPasswordValidator(control: AbstractControl): ValidationErrors | null {

  const value: string = control.value;

  if (!value) {
    return null;
  }
  /*
  * La contraseña debe de aceptar minúsculas, mayúsculas y números. La longitud será mínimo de 1 carácter, además,
  * de que necesita si o si tener 1 min, 1 may, 1 num.
  * */
  const regex_pro = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-z\d]+$/i;
  const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])[a-zA-Z0-9]+$/;

  return regex.test(value) ? null : {customPassword: true};

}
