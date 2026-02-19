import { TestBed } from '@angular/core/testing';

import { AlertServices } from './alert.services';

describe('AlertServices', () => {
  let service: AlertServices;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AlertServices);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
