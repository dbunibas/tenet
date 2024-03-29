import { Injectable } from '@angular/core';
import {
  Router, Resolve,
  RouterStateSnapshot,
  ActivatedRouteSnapshot
} from '@angular/router';
import { Observable, of, single } from 'rxjs';
import { ExportDaoService } from '../dao/export-dao.service';
import { ModelService } from '../model.service';
import { MessagesService } from '../utilities/messages.service';
import { Export } from 'src/app/model/export';
import { C } from '../c';

@Injectable({
  providedIn: 'root'
})
export class ExportsResolver implements Resolve<void> {

  constructor(
    private exportDAO: ExportDaoService,
    private model: ModelService,
    private messages: MessagesService,
    private router: Router
  ) { }

  async resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {

    try {
      let exports = await this.exportDAO.getExports()

      console.log("Loaded ", exports.length, " exports");

      let exportsMap = new Map<string, Export[]>();

      for (let singleExport of exports) {
        if (!exportsMap.has(singleExport.projectName)) {
          exportsMap.set(singleExport.projectName, []);
        }
        exportsMap.get(singleExport.projectName)!.push(singleExport);
      }
      this.model.putBean(C.EXPORTS_MAP, exportsMap);
    }
    catch (error) {
      console.log(error);
      this.messages.showErrorMessage("Error loading exports");
      this.router.navigate(["/"]);
    };

  }
}
