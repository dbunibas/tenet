import {Component, OnInit} from '@angular/core';
import {FormControl, FormGroup, Validators} from '@angular/forms';
import {Router} from '@angular/router';
import {Database} from 'src/app/model/database';
import {Project} from 'src/app/model/project';
import {C} from 'src/app/service/c';
import {ProjectDaoService} from 'src/app/service/dao/project-dao.service';
import {MessagesService} from 'src/app/service/utilities/messages.service';
import {ModelService} from 'src/app/service/model.service';
import {CSVLoaderService} from "../../service/utilities/csv-loader.service";

@Component({
  selector: 'app-new-project',
  templateUrl: './new-project.component.html',
  styleUrls: ['./new-project.component.css']
})
export class NewProjectComponent implements OnInit {

  private file: any;

  constructor(
    private messages: MessagesService,
    private model: ModelService,
    private router: Router,
    private projectDAO: ProjectDaoService,
    private csvLoader: CSVLoaderService
  ) {
  }

  ngOnInit(): void {
    console.log("Showing new project page");
    this.model.removePersistentBean(C.TABLE);
    this.model.removeBean(C.TABLE);
  }

  get existingProjects() {
    return this.model.getBean<Project[]>(C.PROJECTS)!;
  }

  formLoadScenario = new FormGroup({
    scenario: new FormControl<string>('', Validators.required)
  });

  formCreate = new FormGroup({
    file: new FormControl(null, [
      Validators.required,
    ]),
    name: new FormControl<string>('', [
      Validators.required,
      Validators.minLength(5)
    ])
  });

  get scenarioField() {
    return this.formLoadScenario.get("scenario")!;
  }

  get nameField() {
    return this.formCreate.get("name")!;
  }

  get fileField() {
    return this.formCreate.get("file")!;
  }

  fileChange(event: any) {
    this.file = event.target.files[0];
    if ((this.file as File).type !== "text/csv") {
      this.fileField.setErrors({"invalid-file": true});
    }
  }

  loadExistingScenario() {
    let projectId = this.scenarioField.value!;
    console.log("Loading ", projectId);
    this.model.putPersistentBean(C.SELECTED_PROJECT_ID, projectId);
    this.router.navigate(["/project"]);
  }

  createFromCSV() {
    this.model.showLoadingSpinner();
    this.csvLoader.readTableFromFile(this.file, (table) => {
      this.model.hideLoadingSpinnner();
      let newProject = new Project(this.nameField.value!, new Database(table));
      console.log("Loaded ", table.cells.length, "cells");
      this.projectDAO.createProject(newProject).then((project: Project) => {
        this.messages.showInfoMessage("Project created");
        console.log("Created project with id: " + project.id);
        this.model.putPersistentBean(C.SELECTED_PROJECT_ID, project.id);
        this.router.navigate(["/project"]);
      }).catch(error => this.messages.showErrorMessage(error));
    });

  }


}

