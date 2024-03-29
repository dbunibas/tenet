import {Injectable} from '@angular/core';
import {Table} from "../../model/table";
import {Header} from "../../model/header";
import {Cell} from "../../model/cell";
import {Papa} from "ngx-papaparse";

@Injectable({
  providedIn: 'root'
})
export class CSVLoaderService {

  constructor(private paParse: Papa) {
  }

  private parseTable(csvText: string): Table {

    csvText = csvText.trim();
    if (csvText.length === 0) {
      throw Error("Empty CSV");
    }
    let fieldSeparator = this.findSeparator(csvText);
    console.log("Parsing CSV with separator '", fieldSeparator,"'");
    // const result = this.paParse.parse(csvText, {header: true});
    // console.log(result)
    // let newTable = new Table();
    // for (let h of result.meta.fields) {
    //   let newHeader = new Header(h.trim());
    //   newTable.schema.push(newHeader);
    // }
    // let cellId = 0;
    // let row = 0;
    // for (let rowData of result.data) {
    //   let column = 0;
    //   for (let col of Object.keys(rowData)) {
    //     let header = newTable.schema[column];
    //     let value = rowData[header.name];
    //     console.log("VALUE: ", value)
    //     console.log("Type of value: ", typeof value)
    //     let cell = new Cell(header, row, column, value);
    //     cell.cellId = cellId++;
    //     newTable.cells.push(cell);
    //     column++;
    //   }
    //   row++;
    // }
    // console.log(newTable);
    // return newTable;
    let row = 0;
    let newTable = new Table();
    for (let stringRow of csvText.split("\n")) {
      let column = 0;
      if (newTable.schema.length === 0) { // Set headers with the first row

        for (let headerName of stringRow.split(fieldSeparator)) {
          let newHeader = new Header(headerName.trim());
          newTable.schema.push(newHeader);
        }
      } else {
        for (let value of stringRow.split(fieldSeparator)) {

          let header = newTable.schema[column];
          let cell = new Cell(header, row, column, value.trim());
          newTable.cells.push(cell);
          column++;
        }
        row++;
      }
    }
    console.log(newTable);
    return newTable;
  }

  private findSeparator(csv: string): string {
    let separator: string = ",";
    if (!(csv.split("\n")[0].split(separator).length > 1)) {
      separator = ";";
    }
    return separator;
  }

  public readTableFromFile(file: any, callback: (table: Table) => void) {
    const fileReader = new FileReader();
    fileReader.readAsText(file);
    fileReader.onload = () => {
      let table = this.parseTable(fileReader.result!.toString());
      callback(table);
    }
  }

}
