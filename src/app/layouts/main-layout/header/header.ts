import {Component, OnInit, signal} from '@angular/core';
import {Login} from '../login/login'
import {Register} from '../register/register'

import {ContenPrincipal} from '../conten-principal/conten-principal';

@Component({
  selector: 'app-header',
  imports: [Login, Register, ContenPrincipal],
  templateUrl: './header.html',
  styleUrl: './header.scss',
  standalone: true

})
export class Header  {

  openLogin = signal<boolean>(false);

  toogleLogin() {
    this.openLogin.update(v => !v)
  }

  openRegister = signal<boolean>(false);

  toggleRegister() {
    this.openRegister.update(v => !v)
  }



}
