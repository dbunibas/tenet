import {Injectable} from '@angular/core';
import {ActivatedRouteSnapshot, Resolve, RouterStateSnapshot} from '@angular/router';
import {ModelService} from '../model.service';
import {ProjectDaoService} from '../dao/project-dao.service';
import {MessagesService} from '../utilities/messages.service';
import {C} from '../c';
import {Project} from 'src/app/model/project';

@Injectable({
  providedIn: 'root'
})
export class ProjectsResolver implements Resolve<void> {

  constructor(
    private model: ModelService,
    private projectDAO: ProjectDaoService,
    private messages: MessagesService
  ) {
  }

  async resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Promise<void> {

    try {
      let projects: Project[] = await this.projectDAO.getProjects();
      console.log(projects.length + " existing projects found");
      this.model.putBean(C.PROJECTS, projects);
    } catch (e) {
      this.messages.showErrorMessage("Can't retrieve existing projects");
    }

  }
}
