import {ApplicationRef, ComponentRef, EmbeddedViewRef, Injectable} from '@angular/core';
import {AppComponent} from '../../app.component';
import {SnackbarComponent} from '../../components/snackbar/snackbar.component';

@Injectable({
  providedIn: 'root'
})
export class MessagesService {

  private opened = false;
  private componentRef?: ComponentRef<SnackbarComponent>;
  private closeTimeout?: any;

  constructor(private appRef: ApplicationRef) {
  }

  showErrorMessage(error: string): void {
    this.open(error, 3000, undefined, 'var(--bs-danger)');
  }

  showInfoMessage(message: string): void {
    this.open(message, 3000, undefined, 'var(--bs-success)');
  }

  private open(message: string, timeout: number = 5000, selector?: string, backgroundColor?: string) {
    this.openSnackBar(timeout, {
      message
    }, selector, backgroundColor);
  }

  private openSnackBar(timeout: number, {message}: { message: string }, selector: string = 'app-root',
                       backgroundColor?: string, textColor?: string) {
    if (this.opened) {
      this.closeSnackbar(0, {message, timeout, selector, backgroundColor});
      return;
    }
    this.componentRef = (this.appRef.components[0].instance as AppComponent).viewContainerRef?.createComponent(SnackbarComponent)!;
    this.componentRef.instance.message = message;
    this.componentRef.instance.bgColor = backgroundColor ?? getComputedStyle(document.body).getPropertyValue('--bg-snackbar');
    this.componentRef.instance.textColor = textColor ?? getComputedStyle(document.body).getPropertyValue('--text-snackbar');

    const element = (this.componentRef.hostView as EmbeddedViewRef<any>).rootNodes[0] as HTMLElement;
    document.querySelector(selector)?.appendChild(element);
    this.opened = true;

    this.closeSnackbar(timeout);
  }

  private closeSnackbar(timeout: number, reopenSnackBarParams?: {
    message: string,
    timeout: number,
    selector: string,
    backgroundColor?: string
  }) {
    if (!!reopenSnackBarParams) {
      clearTimeout(this.closeTimeout);
    }
    this.closeTimeout = setTimeout(() => {
      if (!this.componentRef) return;
      this.appRef.detachView(this.componentRef.hostView);
      this.opened = false;
      if (!!reopenSnackBarParams) {
        const {message, timeout, selector, backgroundColor} = reopenSnackBarParams;
        this.open(message, timeout, selector, backgroundColor);
      }
    }, timeout);
  }

}
