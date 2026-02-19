import { TestBed } from '@angular/core/testing';

import { ReposSinRegistroService } from './repos-sin-registro.service';

describe('ReposSinRegistroService', () => {
  let service: ReposSinRegistroService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ReposSinRegistroService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
