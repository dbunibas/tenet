import { Component } from '@angular/core';
import { Export } from 'src/app/model/export';
import { C } from 'src/app/service/c';
import { ExportDaoService } from 'src/app/service/dao/export-dao.service';
import { ModelService } from 'src/app/service/model.service';
import { ExportService } from 'src/app/service/utilities/export.service';
import { MessagesService } from 'src/app/service/utilities/messages.service';

@Component({
  selector: 'app-exports',
  templateUrl: './exports.component.html',
  styleUrls: ['./exports.component.scss']
})
export class ExportsComponent {

  exportsArray: [string, Export[]][] = [];

  constructor(private model: ModelService, private exportService: ExportService,
    private exportDAO: ExportDaoService, private messages: MessagesService) {
    this.exportsArray = Array.from(this.model.getBean(C.EXPORTS_MAP)!);
  }

  download(ex: Export) {
    console.log("downloading export: ", ex.id);
    this.exportDAO.getExport(ex.id).then(result => {
      this.exportService.downloadExport(result, ex.projectName);
    }).catch( error => {
      console.log(error);
      this.messages.showErrorMessage("Error downloading the export file");
    });
  }
}
