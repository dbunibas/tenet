import {Injectable} from '@angular/core';
import { ModelService } from '../model.service';
import { MessagesService } from './messages.service';
import { C } from '../c';
import { ProjectDaoService } from '../dao/project-dao.service';
import { Subscription, interval, switchMap, timer } from 'rxjs';
import { Project } from 'src/app/model/project';
import { ExportDaoService } from '../dao/export-dao.service';

@Injectable({
  providedIn: 'root'
})
export class ExportService {

  private POLLING_TIME: number = 5000;

  constructor(private model: ModelService, private messages: MessagesService,
    private projectDAO: ProjectDaoService, private exportDAO: ExportDaoService) {
    let activeExportId = this.model.getPersistentBean<string>(C.EXPORT_ID);
    if (activeExportId) {
      console.log("Exporting in progress");
      this.setExportingMode(true);
      this.startPolling(activeExportId);
    }
  }


  private polling?: Subscription;


  startExport(positiveNumber: number, negativeNumber: number, sentencesNumber: number) {
    const projectId = this.model.getPersistentBean<string>(C.SELECTED_PROJECT_ID)!;
    this.projectDAO.startExport(projectId, positiveNumber, negativeNumber, sentencesNumber).then(
      result => {
        console.log("Started export with id: " + result);
        this.model.putPersistentBean(C.EXPORT_ID, result);
        this.setExportingMode(true);
        this.startPolling(result);
      }).catch(error => {
        this.messages.showErrorMessage("Export failed: " + error);
        console.log(error);
      });
  }

  private startPolling(exportId: string) {
    this.polling = interval(this.POLLING_TIME).subscribe(() => {
      this.doPolling(exportId);
    });
  }

  private doPolling(exportId: string) {
    console.log("Polling...");
    this.exportDAO.getExport(exportId, true).then( result => {
      if (result !== null) {
        this.messages.showInfoMessage("Export completed");
        this.polling!.unsubscribe();
        this.downloadExport(result, this.model.getBean<Project>(C.ACTIVE_PROJECT)!.name);
        this.model.removePersistentBean(C.EXPORT_ID);
        this.setExportingMode(false);

      }
      console.log("Result length: ",result?.length);
    }).catch(error => {
      this.messages.showErrorMessage("Error in examples generation");
      console.log(error);
      this.setExportingMode(false);
      this.model.removePersistentBean(C.EXPORT_ID);
      this.polling!.unsubscribe();
    });
  }

  public downloadExport(json: string, fName: string = "") {
    const filename = fName + "-export.json";
    var element = document.createElement('a');
    element.setAttribute('href', "data:text/json;charset=UTF-8," + encodeURIComponent(json));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  }

  private setExportingMode(exporting: boolean) {
    this.model.putBean(C.EXPORTING, exporting);
  }
}
