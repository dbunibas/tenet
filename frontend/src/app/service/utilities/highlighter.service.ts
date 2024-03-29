import {Injectable} from '@angular/core';
import 'prismjs';
import 'prismjs/plugins/toolbar/prism-toolbar';
import 'prismjs/components/prism-sql';

declare var Prism: any;

@Injectable({
  providedIn: 'root'
})
export class HighlighterService { // Code highlighting with PrismJS

  constructor() {
  }

  highlightAll() {
    Prism.highlightAll();
  }


}
