import {AbstractControl,ValidationErrors} from '@angular/forms';


export function EmailValidator(control:AbstractControl): ValidationErrors | null{
  const value=control.value;
  if (!value){
    return null;
  }
  const regex1 = /@(gmail|hotmail)(\.)/;

  if (!regex1.test(value)) {
    return {extension: true}
  }
  const regex2 = /^[a-z0-9._-]{3,}(@)(gmail|hotmail)(\.)(com|es)$/i;
  return regex2.test(value) ? null : {customEmail: true};


}
