import {Component, Input} from '@angular/core';
import {user} from 'src/app/model/user';
import {C} from 'src/app/service/c';
import {ModelService} from 'src/app/service/model.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent {

  @Input() public title?: string;

  constructor(private model: ModelService) {
  }

  get user(): user | undefined {
    return this.model.getPersistentBean<user>(C.LOGIN_USER);
  }

  get activeProject(): string | undefined {
    return this.model.getPersistentBean<string>(C.SELECTED_PROJECT_ID);
  }

}
