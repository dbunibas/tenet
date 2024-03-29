import {ChangeDetectionStrategy, Component} from '@angular/core';
import {animate, group, query, style, transition, trigger} from "@angular/animations";
import {CommonModule} from "@angular/common";

export const SNACKBAR_ANIMATION_DURATION = 400;

const hiddenTransform = 'translate(50%, 20%) scale(0.8)';
const visibleTransform = 'translate(50%, -30%) scale(1)';
const visibleStyling = {opacity: 1, transform: visibleTransform};
const hiddenStyling = {opacity: 0, transform: hiddenTransform};
const cubicBezier = 'cubic-bezier(.71,.72,.03,1.43)';
const animationTiming = `${SNACKBAR_ANIMATION_DURATION}ms ${cubicBezier}`;

@Component({
  standalone: true,
  imports: [CommonModule],
  selector: 'app-snack-bar',
  templateUrl: './snackbar.component.html',
  styleUrls: ['./snackbar.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  animations: [
    trigger('host', [
      transition(':enter', [
        group([
          query('.snackbar', [
            style(hiddenStyling),
            animate(animationTiming, style(visibleStyling))
          ]),
        ]),
      ]),
      transition(':leave', [
        group([
          query('.snackbar', [
            animate(animationTiming, style(hiddenStyling))
          ]),
        ]),
      ]),
    ]),
  ],
  host: {'[@host]': ''}
})
export class SnackbarComponent {
  message?: string;
  bgColor?: string;
  textColor?: string;

  constructor() {
  }

}
