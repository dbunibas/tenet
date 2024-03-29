import {Component, HostListener} from '@angular/core';
import {ModelService} from "../../service/model.service";
import {Project} from "../../model/project";
import {C} from "../../service/c";

@Component({
  selector: 'app-project',
  templateUrl: './project.component.html',
  styleUrls: ['./project.component.css']
})
export class ProjectComponent {

  constructor(private model: ModelService) {
  }


  get project(): Project {
    return this.model.getBean<Project>(C.ACTIVE_PROJECT)!;
  }

}
