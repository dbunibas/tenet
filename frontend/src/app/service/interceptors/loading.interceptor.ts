import {Injectable} from '@angular/core';
import {HttpContextToken, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';
import {finalize, Observable} from 'rxjs';
import {ModelService} from '../model.service';
import {C} from '../c';

export const BYPASS_LOADING = new HttpContextToken(() => false);

@Injectable()
export class LoadingInterceptor implements HttpInterceptor {

  constructor(private model: ModelService) {
  }

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    if (request.context.get(BYPASS_LOADING) === true) {
      return next.handle(request);
    }
    this.model.putBean(C.LOADING, true);
    return next.handle(request).pipe(
      finalize(() => this.model.removeBean(C.LOADING))
    );
  }
}
