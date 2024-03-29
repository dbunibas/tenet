import {Injectable} from '@angular/core';
import {HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';
import {Observable} from 'rxjs';
import {ModelService} from '../model.service';
import {C} from '../c';
import {user} from 'src/app/model/user';

@Injectable()
export class AuthTokenInterceptor implements HttpInterceptor {

  constructor(private model: ModelService) {
  }

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const loginUser = this.model.getPersistentBean<user>(C.LOGIN_USER);
    if (loginUser) {
      request = request.clone({
        setHeaders: {
          Authorization: `Bearer ${loginUser.authToken}`
        }
      });
    }
    return next.handle(request);
  }
}
