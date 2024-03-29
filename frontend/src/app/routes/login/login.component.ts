import {Component, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {Router} from '@angular/router';
import {C} from 'src/app/service/c';
import {UserDAOService} from 'src/app/service/dao/user-dao.service';
import {MessagesService} from 'src/app/service/utilities/messages.service';
import {ModelService} from 'src/app/service/model.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  animations: []
})
export class LoginComponent implements OnInit {

  ngOnInit(): void {
    this.model.clear();
  }

  constructor(private model: ModelService,
              private messages: MessagesService,
              private userDAO: UserDAOService,
              private router: Router) {
  }


  loginForm = new FormGroup({
    username: new FormControl<string>('', Validators.required),
    password: new FormControl<string>('', Validators.required)
  });

  get usernameField() {
    return this.loginForm.get("username")!;
  }

  get passwordField() {
    return this.loginForm.get("password")!;
  }

  login() {
    let username: string = this.usernameField.value!;
    let password: string = this.passwordField.value!;
    console.log("Login attempt with credentials ", username, " ", password);
    this.userDAO.login(username, password).then(user => {
      this.model.putPersistentBean(C.LOGIN_USER, user);
      this.router.navigate(["/"]);
    })
      .catch(error => {
        this.messages.showErrorMessage(error);
      })
  }

}
