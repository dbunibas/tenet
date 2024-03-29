import {Component} from "@angular/core";
import {user} from "src/app/model/user";
import {C} from "src/app/service/c";
import {ModelService} from "src/app/service/model.service";

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.css']
})
export class FooterComponent {

  constructor(private model: ModelService) {
  }

  get user(): user | undefined {
    return this.model.getPersistentBean<user>(C.LOGIN_USER);
  }

}
