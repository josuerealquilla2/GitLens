import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RepositoriosPorLenguaje } from './repositorios-por-lenguaje';

describe('RepositoriosPorLenguaje', () => {
  let component: RepositoriosPorLenguaje;
  let fixture: ComponentFixture<RepositoriosPorLenguaje>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RepositoriosPorLenguaje]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RepositoriosPorLenguaje);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
