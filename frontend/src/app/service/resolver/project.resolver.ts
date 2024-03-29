import {Injectable} from '@angular/core';
import {ActivatedRouteSnapshot, Resolve, Router, RouterStateSnapshot} from '@angular/router';
import {ModelService} from "../model.service";
import {MessagesService} from "../utilities/messages.service";
import {C} from "../c";
import {ProjectDaoService} from "../dao/project-dao.service";

@Injectable({
  providedIn: 'root'
})
export class ProjectResolver implements Resolve<void> {

  constructor(
    private model: ModelService,
    private router: Router,
    private messages: MessagesService,
    private projectDAO: ProjectDaoService
  ) {
  }

  async resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    let projectId = this.model.getPersistentBean<string>(C.SELECTED_PROJECT_ID);
    if (!projectId) {
      await this.router.navigate(["/new"]);
      return;
    }
    try {
      let project = await this.projectDAO.getProject(projectId);
      console.log("Loaded project ", project.database.table.cells.length, " cells");
      project.buildRows();
      console.log(project.database.table.rows.length, " rows");

      this.model.putBean(C.ACTIVE_PROJECT, project);
    } catch (error) {
      this.messages.showErrorMessage("Error loading project: " + error);
      console.log(error);
      this.model.removePersistentBean(C.SELECTED_PROJECT_ID);
      await this.router.navigate(["/new"]);
    }


  }


}
