import {Injectable} from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ScrollService {

  constructor() {
  }

  public scrollTo(selector: string) {
    const evidenceListBlock = document.querySelector(selector);
    setTimeout(() => evidenceListBlock?.scrollIntoView({behavior: "smooth", block: "start", inline: "nearest"}), 500);

  }
}
