import {HttpClient} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {lastValueFrom, tap} from 'rxjs';
import {user} from 'src/app/model/user';
import {environment} from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UserDAOService {

  constructor(private httpClient: HttpClient) {
  }

  login(username: string, password: string): Promise<user> {
    let apiURL = environment.backendUrl + '/users/login';
    return lastValueFrom(
      this.httpClient.post<user>(apiURL, {username: username, password: password})
        .pipe(
          tap(response => {
            console.log('Response: ', response);
            if (!response) throw new Error("Failed to fetch authToken");
          })
        )
    );
  }
}
