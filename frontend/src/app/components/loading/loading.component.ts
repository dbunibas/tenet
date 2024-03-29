import {Component} from '@angular/core';
import {C} from 'src/app/service/c';
import {ModelService} from 'src/app/service/model.service';

@Component({
  selector: 'app-loading',
  templateUrl: './loading.component.html',
  styleUrls: ['./loading.component.css']
})
export class LoadingComponent {

  constructor(private model: ModelService) {
  }

  get loading(): boolean {
    return this.model.getBean(C.LOADING) === true;
  }

}
