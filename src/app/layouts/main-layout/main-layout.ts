import {Component} from '@angular/core';
import {Header} from './header/header';
import {Footer} from './footer/footer';

@Component({
  selector: 'app-main-layout',
  imports: [
    Header,
    Footer
  ],
  templateUrl: './main-layout.html',
  styleUrl: './main-layout.scss',
})
export class MainLayout{}


