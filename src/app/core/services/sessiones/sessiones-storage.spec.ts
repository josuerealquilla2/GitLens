import { TestBed } from '@angular/core/testing';

import { SessionesStorage } from './sessiones-storage';

describe('SessionesStorage', () => {
  let service: SessionesStorage;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SessionesStorage);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
