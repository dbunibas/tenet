import {Injectable} from '@angular/core';
import {ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree} from '@angular/router';
import {Observable} from 'rxjs';
import {user} from '../model/user';
import {C} from '../service/c';
import {ModelService} from '../service/model.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(private router: Router, private model: ModelService) {
  }

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    let loginUser = this.model.getPersistentBean<user>(C.LOGIN_USER);
    if (loginUser && loginUser.authToken) {
      return true;
    }
    console.log('Access not allowed ', route.url[0].path);
    this.router.navigate(['/login']);
    return false;
  }

}
