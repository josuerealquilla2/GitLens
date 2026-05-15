import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContenPrincipal } from './conten-principal';

describe('ContenPrincipal', () => {
  let component: ContenPrincipal;
  let fixture: ComponentFixture<ContenPrincipal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContenPrincipal]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ContenPrincipal);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
