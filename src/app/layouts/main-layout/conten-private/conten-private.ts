import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HeaderPrivado } from './header-privado/header-privado';
import { RepositoriosPorLenguaje } from './repositorios-por-lenguaje/repositorios-por-lenguaje';
import { SeccionTendencias } from './seccion-tendencias/seccion-tendencias';
import { SeccionFavoritos } from './seccion-favoritos/seccion-favoritos';
import { SeccionGuardados } from './seccion-guardados/seccion-guardados';
import { SeccionHistorial } from './seccion-historial/seccion-historial';
import { Profile } from './profile/profile';
import { SeccionAmigos } from './seccion-amigos/seccion-amigos';
import { SeccionChat } from './seccion-chat/seccion-chat';
import { NavigationService } from '../../../core/services/navigation/navigation.service';

@Component({
  selector: 'app-conten-private',
  standalone: true,
  imports: [
    CommonModule,
    HeaderPrivado,
    RepositoriosPorLenguaje,
    SeccionTendencias,
    SeccionFavoritos,
    SeccionGuardados,
    SeccionHistorial,
    Profile,
    SeccionAmigos,
    SeccionChat,
  ],
  templateUrl: './conten-private.html',
  styleUrl: './conten-private.scss',
})
export class ContenPrivate {
  constructor(public navService: NavigationService) {}
}
