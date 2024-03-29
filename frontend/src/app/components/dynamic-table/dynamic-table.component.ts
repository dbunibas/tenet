import {Component, Input, OnInit} from '@angular/core';
import {MtxGridColumn, MtxGridColumnType, MtxGridRowClassFormatter} from '@ng-matero/extensions/grid';
import {ModelService} from 'src/app/service/model.service';
import {Table} from 'src/app/model/table';
import {Project} from "../../model/project";
import {Cell} from "../../model/cell";
import {Evidence} from "../../model/evidence";
import {MessagesService} from "../../service/utilities/messages.service";
import {C} from "../../service/c";
import {Sort} from "@angular/material/sort";
import {EvidenceDAOService} from "../../service/dao/evidence-dao.service";
import {ScrollService} from "../../service/utilities/scroll.service";

@Component({
  selector: 'app-dynamic-table',
  templateUrl: './dynamic-table.component.html',
  styleUrls: ['./dynamic-table.component.css']
})
export class DynamicTableComponent implements OnInit {

  @Input("project")
  public project!: Project;

  get exporting(): boolean {
    return this.model.getBean(C.EXPORTING)!;
  }

  ngOnInit(): void {
    let orderedColumns: string[] = [];
    for (let header of this.table.schema) {
      let cType: MtxGridColumnType | undefined = undefined;
      orderedColumns.push(header.name);
      this.columns.push({
        header: header.name,
        field: header.name,
        type: cType,
        sortable: true,
        resizable: true,
        buttons: [
          {
            type: "basic",
            text: "Select"
          }
        ],
      });
    }
    this.dataSource = this.table.rows;
    this.model.putBean(C.ORDERED_COLUMNS, orderedColumns);

    // Setting rows and columns selected
    if (this.project.findUserEvidence() === undefined) {
      return;
    }
    for (let col of this.columns) {
      let selected = true;
      for (let row of this.dataSource) {
        if (!row[col.field].selected) {
          selected = false;
          break;
        }
      }
      if (selected) {
        this.selectedColumns.push(col.field);
      }
    }
    for (let row of this.dataSource) {
      if (!Object.keys(row).find(key => !row[key].selected)) {
        this.selectedRows.push(row);
      }
    }
  }

  constructor(private model: ModelService,
              private messages: MessagesService,
              private evidenceDAO: EvidenceDAOService,
              private scroll: ScrollService) {
  }

  dataSource: any[] = [];

  columns: MtxGridColumn[] = [];

  selectedColumns: string[] = [];
  selectedRows: any = [];

  filterString = "";
  filterProperty = "";

  rowFormatter: MtxGridRowClassFormatter = {
    selectionStyle: (data, index) => true
  }



  applyFilter() {
    this.dataSource = this.project.getFilteredRows(this.filterProperty, this.filterString);
  }

  get table(): Table {
    return this.project.database.table;
  }

  trackByName(index: number, item: any) {
    return item.name;
  }

  updateRowSelection(currentRowSelection: Array<any>) {
    if (currentRowSelection.length === 0) { // Nothing selected
      for (let row of this.selectedRows) {
        this.setRowCellsSelection(row, false);
      }
      this.selectedColumns = [];
      this.selectedRows = [];
      return;
    } else if (currentRowSelection.length === this.dataSource.length) { // All selected
      this.columns.forEach(col => this.selectedColumns.push(col.field));
    }
    for (let row of this.selectedRows) {
      if (!currentRowSelection.includes(row)) {
        this.setRowCellsSelection(row, false);
        this.removeElement(this.selectedRows, row);
        this.removeColumnSelectionByRow(row);
      }
    }
    for (let row of currentRowSelection) {
      if (!this.selectedRows.includes(row)) { // Select row
        this.selectRow(row);
      }
    }
  }

  private selectRow(row: any) {
    this.setRowCellsSelection(row, true);
    this.selectedRows.push(row);
    for (let key of Object.keys(row)) {
      let columnName = row[key].header.name;
      if (!this.dataSource.find(row => !row[columnName].selected)) {
        this.selectedColumns.push(columnName);
      }
    }
  }

  private removeColumnSelectionByRow(row: any) { //
    for (let key of Object.keys(row)) {
      if (this.selectedColumns.includes(key)) {
        this.selectedColumns = this.selectedColumns.filter((col) => col != key);
      }
    }
  }

  private setRowCellsSelection(row: any, selected: boolean) {
    for (let key of this.table.schema) {
      row[key.name].selected = selected;
    }
  }

  toggleCell(cell: Cell) {
    cell.selected = !cell.selected;
    let columnName = cell.header.name;
    const cellRow = this.table.rows.at(cell.row);
    if (cell.selected) {
      if (!this.dataSource.find(row => !row[columnName].selected)) {
        this.selectedColumns.push(columnName);
      }
      if (!Object.keys(cellRow).find(key => !cellRow[key].selected)) { // if all cells in the row are selected
        this.selectedRows = [...this.selectedRows, cellRow];
      }
    } else {
      if (this.selectedRows.includes(cellRow)) {
        this.selectedRows = this.selectedRows.filter((row: any) => row != cellRow);
      }
      if (this.selectedColumns.includes(columnName)) {
        this.selectedColumns = this.selectedColumns.filter((col) => col != columnName);
      }
    }
  }

  toggleColumn(column: MtxGridColumn): void {
    let selectedValue = true;
    if (this.selectedColumns.includes(column.field)) {
      selectedValue = false;
      this.removeElement(this.selectedColumns, column.field);
    } else {
      this.selectedColumns.push(column.field);
    }
    for (let row of this.dataSource) {
      row[column.field].selected = selectedValue;
      if (!selectedValue && this.selectedRows.includes(row)) {
        this.selectedRows = this.selectedRows.filter((r: any) => r != row);
      }
      if (selectedValue) {
        if (!Object.keys(row).find(key => !row[key].selected)) { // if all cells in the row are selected
          this.selectedRows = [...this.selectedRows, row];
        }
      }
    }
  }

  sendEvidence() {
    let selectedCells: Cell[] = [];
    for (let cell of this.table.cells) {
      if (cell.selected) {
        selectedCells.push(cell);
      }
    }
    if (selectedCells.length === 0) {
      this.messages.showErrorMessage("Nothing selected");
      return;
    }
    console.log(selectedCells.length," cell selected");
    if (!this.project.evidence || this.project.evidence.length === 0) { // Create first evidence
      if (this.project.evidence === null) {
        this.project.evidence = [];
      }
      let evidence = new Evidence(selectedCells);
      this.evidenceDAO.createEvidence(this.project.id!, evidence).then(newEvidence => {
        this.messages.showInfoMessage("Evidence sent");
        this.project.evidence.push(newEvidence);
      }).catch(error => this.messages.showErrorMessage(error));
    } else { // Update existing user evidence
      let evidence: Evidence = this.project.findUserEvidence()!;
      evidence.cells = selectedCells;
      this.evidenceDAO.updateEvidence(this.project.id!, evidence).then(r => {
        this.messages.showInfoMessage("Evidence updated");
        this.evidenceDAO.getEvidenceList(this.project.id!).then(evidence => {
          this.project.evidence = [];
          evidence.forEach(e => this.project.evidence.push(e));
        }).catch(error => this.messages.showErrorMessage(error));
      }).catch(error => this.messages.showErrorMessage(error));
    }
    this.scroll.scrollTo("#evidence-list");
  }

  sort(sort: Sort) {
    let sortCol = sort.active;
    let direction = sort.direction;
    console.log("Sorting ", sortCol, " ", direction);
    this.dataSource.sort((row1, row2) => {
      let val1 = row1[sortCol].value;
      let val2 = row2[sortCol].value;
      if (!isNaN(Number(val1))) {
        val1 = Number(val1);
        val2 = Number(val2);
      }
      if (direction === "asc") {
        return val1 < val2 ? -1 : 1;
      }
      return val1 > val2 ? -1 : 1;
    })
  }

  colOrderChange(columns: MtxGridColumn[]) {
    let orderedColumns: string[] = columns.map(col => col.field);
    this.model.putBean(C.ORDERED_COLUMNS, orderedColumns);
  }

  private removeElement(collection: any[], element: any) {
    collection.splice(collection.indexOf(element), 1);
  }

}
