import { Directive, ElementRef, Renderer2, HostListener } from '@angular/core';

@Directive({
  selector: '[appCaret]'
})
export class CaretDirective {
  private svg!: SVGElement;

  constructor(private el: ElementRef, private renderer: Renderer2) {
    const caretSvg = `
      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"
           xmlns="http://www.w3.org/2000/svg" class="caret ms-2">
        <path d="M3 4 L3 6.5 L8 11.5 L13 6.5 L13 4 L8 9 Z"/>
      </svg>
    `;
    this.el.nativeElement.insertAdjacentHTML('beforeend', caretSvg);
  }

  @HostListener('mouseenter') onHover() {
    this.rotateCaret(180);
  }

  @HostListener('mouseleave') onLeave() {
    this.rotateCaret(0);
  }

  private rotateCaret(deg: number) {
    const svg = this.el.nativeElement.querySelector('.caret');
    if (svg) {
      this.renderer.setStyle(svg, 'transform', `rotate(${deg}deg)`);
      this.renderer.setStyle(svg, 'transition', 'transform 0.3s');
    }
  }
}
