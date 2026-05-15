import { Routes } from '@angular/router';
import { authGuard } from './core/guards/authguard/auth.guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import("./layouts/layout-public/layout-public").then(c => c.LayoutPublic),
  },

  {
    path: 'privado',
    canActivate: [authGuard],
    loadComponent:()=> import("./layouts/main-layout/conten-private/conten-private").then(c=>c.ContenPrivate),
  },
];



