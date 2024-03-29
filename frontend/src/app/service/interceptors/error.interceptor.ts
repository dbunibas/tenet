import {HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {Router} from '@angular/router';
import {catchError, Observable, throwError} from 'rxjs';

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {

  constructor(
    private router: Router
  ) {
  }

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(request).pipe(
      catchError(httpError => {
        console.error("ERROR: ", httpError);
        if (httpError instanceof HttpErrorResponse && httpError.error) {
          if (httpError.status === 401) { // Unhautorized -> redirect to login
            this.router.navigate(["/login"]);
            return throwError(() => "Login required")
          }
          if (httpError.status === 0) {
            return throwError(() => "No response from the server");
          }
          if (httpError.error instanceof Object && httpError.error.error) {
            httpError = httpError.error.error;
          } else {
            let backendError = JSON.parse(httpError.error);
            if (backendError['error']) {
              httpError = backendError['error'];
            }
          }
        }
        return throwError(() => httpError);
      })
    );
  }

}
