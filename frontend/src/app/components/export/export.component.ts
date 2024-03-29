import { Component } from '@angular/core';
import {MatProgressBarModule} from '@angular/material/progress-bar';
import { C } from 'src/app/service/c';
import { ModelService } from 'src/app/service/model.service';

@Component({
  selector: 'app-export',
  templateUrl: './export.component.html',
  styleUrls: ['./export.component.scss']
})
export class ExportComponent {

  constructor(private model: ModelService) {}

  get exporting(): boolean {
    return this.model.getBean(C.EXPORTING)!;
  }

}
