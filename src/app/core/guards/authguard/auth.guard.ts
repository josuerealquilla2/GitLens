import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthCookieService } from '../../services/cookies/authcookies.service';

export const authGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  const cookiesService = inject(AuthCookieService);

  const token = cookiesService.get('gitlens_token');

  if (token) {
    return true;
  } else {
    router.navigate(['/'])
    return false;
  }
};
