import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { Evidence } from "../../../model/evidence";
import { ModelService } from "../../../service/model.service";
import { C } from "../../../service/c";
import { Project } from "../../../model/project";
import { MtxGrid, MtxGridColumn, MtxGridColumnType } from "@ng-matero/extensions/grid";
import { Cell } from 'src/app/model/cell';

@Component({
  selector: 'app-single-evidence',
  templateUrl: './single-evidence.component.html',
  styleUrls: ['./single-evidence.component.css']
})
export class SingleEvidenceComponent implements OnChanges {

  @Input()
  public evidence?: Evidence;


  ngOnChanges(changes: SimpleChanges) {
    this.updateTableData();
  }

  constructor(private model: ModelService) {
  }

  // Properties for table data binding
  public SHOWED_ROWS: any[] = [];
  public SHOWED_COLUMNS: MtxGridColumn[] = [];

  private updateTableData(): void {
    let cells = this.evidence!.cells;
    let showedColumnsSet = new Set<string>();
    let orderedColumns = this.model.getBean<string[]>(C.ORDERED_COLUMNS)!;
    for (let cell of cells) {
      showedColumnsSet.add(cell.header.name);
    }
    for (let col of orderedColumns) {
      if (showedColumnsSet.has(col)) {
        this.addToShowedCol(col);
      }
    }
    let prevRow = cells[0].row;
    let rows = new Map<number, any>;
    for (let cell of cells) { // Building DataRows for the table
      if (!rows.has(cell.row)) {
        rows.set(cell.row, {});
      }
      rows.get(cell.row)[cell.header.name.toString()] = cell.value;
    }
    this.SHOWED_ROWS = Array.from(rows.values());
  }

  trackByName(index: number, item: any) {
    return item.name;
  }

  private addToShowedCol(col: string): void {
    let cType: MtxGridColumnType | undefined = undefined;
    this.SHOWED_COLUMNS.push({
      header: col,
      field: col,
      type: cType,
    });
  }

  getCellValue(row: any, col: MtxGridColumn) {
    return row[col.field] ? row[col.field] : '';
  }
}
