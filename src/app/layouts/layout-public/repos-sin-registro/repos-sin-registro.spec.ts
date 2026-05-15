import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReposSinRegistro } from './repos-sin-registro';

describe('ReposSinRegistro', () => {
  let component: ReposSinRegistro;
  let fixture: ComponentFixture<ReposSinRegistro>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReposSinRegistro]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ReposSinRegistro);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
