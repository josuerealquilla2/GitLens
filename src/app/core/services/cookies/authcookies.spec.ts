import { TestBed } from '@angular/core/testing';

import { Authcookies } from './authcookies.service';

describe('Authcookies', () => {
  let service: Authcookies;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Authcookies);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
