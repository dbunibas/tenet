import { Component } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ExportService } from 'src/app/service/utilities/export.service';

@Component({
  selector: 'app-export-dialog',
  templateUrl: './export-dialog.component.html',
  styleUrls: ['./export-dialog.component.scss']
})
export class ExportDialogComponent {

  constructor(private exportService: ExportService) {

  }

  exportExamplesForm = new FormGroup({
    positiveNumber: new FormControl<number | undefined>(undefined,
      [Validators.required, Validators.min(0)]),
    negativeNumber: new FormControl<number | undefined>(undefined,
      [Validators.required, Validators.min(0)]),
      sentencesNumber: new FormControl<number | undefined>(undefined, [
        Validators.required, Validators.min(1)
      ])
  });

  get positiveNumber() {
    return this.exportExamplesForm.get("positiveNumber")!;
  }

  get negativeNumber() {
    return this.exportExamplesForm.get("negativeNumber")!;
  }

  get sentencesNumber() {
    return this.exportExamplesForm.get("sentencesNumber")!;
  }

  export() {
    const positiveNumber: number = this.positiveNumber.value!;
    const negativeNumber: number = this.negativeNumber.value!;
    const sentencesNumber: number = this.sentencesNumber.value!;
    this.exportService.startExport(positiveNumber, negativeNumber, sentencesNumber);
  }

}
