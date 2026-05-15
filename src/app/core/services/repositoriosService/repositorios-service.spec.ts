import { TestBed } from '@angular/core/testing';

import { RepositoriosServiceService } from './repositorios-service.service';

describe('RepositoriosServiceService', () => {
  let service: RepositoriosServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RepositoriosServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
