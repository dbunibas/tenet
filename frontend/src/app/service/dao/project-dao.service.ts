import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { lastValueFrom, map } from 'rxjs';
import { Project } from 'src/app/model/project';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ProjectDaoService {

  constructor(private httpClient: HttpClient){}

  private baseUrl = environment.backendUrl + "/projects";

  getProjects(): Promise<Project[]> {
    return lastValueFrom(this.httpClient.get<Project[]>(this.baseUrl));
  }

  createProject(newProject: Project): Promise<Project> {
    return lastValueFrom(this.httpClient.post<Project>(this.baseUrl, newProject));
  }

  getProject(projectId: string): Promise<Project> {
    let url = `${this.baseUrl}/${projectId}`;
    return lastValueFrom(this.httpClient.get<Project>(url).pipe(map(project => {
      let prj = new Project(project.name, project.database, project.evidence);
      prj.id = project.id;
      return prj;
    })));
  }

  startExport(projectId: string, positiveNumber: number, negativeNumber: number, sentencesNumber: number): Promise<string> {
    let url = `${this.baseUrl}/${projectId}/exports`;
    return lastValueFrom(this.httpClient.post(url, {
      "positiveNumber": positiveNumber,
      "negativeNumber": negativeNumber,
      "sentencesNumber": sentencesNumber
    }, {responseType: "text"}));
  }

}
