import { Component } from '@angular/core';
import {ReposSinRegistro} from '../repos-sin-registro/repos-sin-registro';

@Component({
  selector: 'app-conten-principal',
  imports: [
    ReposSinRegistro
  ],
  templateUrl: './conten-principal.html',
  styleUrl: './conten-principal.scss',
})
export class ContenPrincipal {

}
