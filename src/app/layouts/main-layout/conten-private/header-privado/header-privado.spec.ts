import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HeaderPrivado } from './header-privado';

describe('HeaderPrivado', () => {
  let component: HeaderPrivado;
  let fixture: ComponentFixture<HeaderPrivado>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HeaderPrivado]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HeaderPrivado);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
