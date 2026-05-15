import { Component } from '@angular/core';
import {Header} from './header/header';

import {Footer} from './footer/footer';
import {ContenPrincipal} from './conten-principal/conten-principal';
import {RouterOutlet} from '@angular/router';

@Component({
  selector: 'app-layout-public',
  imports: [
    Header,
    Footer,
    ContenPrincipal,
    RouterOutlet
  ],
  templateUrl: './layout-public.html',
  styleUrl: './layout-public.scss',
  standalone:true,
})
export class LayoutPublic {

}
