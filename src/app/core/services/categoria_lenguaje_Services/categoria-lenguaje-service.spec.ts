import { TestBed } from '@angular/core/testing';

import { CategoriaLenguajeServiceService } from './categoria-lenguaje-service.service';

describe('CategoriaLenguajeServiceService', () => {
  let service: CategoriaLenguajeServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CategoriaLenguajeServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
