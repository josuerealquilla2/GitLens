import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContenPrivate } from './conten-private';

describe('ContenPrivate', () => {
  let component: ContenPrivate;
  let fixture: ComponentFixture<ContenPrivate>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContenPrivate]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ContenPrivate);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
