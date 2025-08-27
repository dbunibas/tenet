import {Injectable} from '@angular/core';
import {Table} from "../../model/table";
import {Header} from "../../model/header";
import {Cell} from "../../model/cell";
import {Papa} from "ngx-papaparse";
import {CsvParser} from "csv-parser"


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
    let rows = this.parseCSV(csvText);
    return this.generateTable(rows);
    
    //let fieldSeparator = this.findSeparator(csvText);
    //console.log("Parsing CSV with separator '", fieldSeparator,"'");
    
    //// const result = this.paParse.parse(csvText, {header: true});
    //// console.log(result)
    //// let newTable = new Table();
    //// for (let h of result.meta.fields) {
    ////   let newHeader = new Header(h.trim());
    ////   newTable.schema.push(newHeader);
    //// }
    //// let cellId = 0;
    //// let row = 0;
    //// for (let rowData of result.data) {
    ////   let column = 0;
    ////   for (let col of Object.keys(rowData)) {
    ////     let header = newTable.schema[column];
    ////     let value = rowData[header.name];
    ////     console.log("VALUE: ", value)
    ////     console.log("Type of value: ", typeof value)
    ////     let cell = new Cell(header, row, column, value);
    ////     cell.cellId = cellId++;
    ////     newTable.cells.push(cell);
    ////     column++;
    ////   }
    ////   row++;
    //// }
    //// console.log(newTable);
    //// return newTable;
    
//    let row = 0;
//    let newTable = new Table();
//    for (let stringRow of csvText.split("\n")) {
//      let column = 0;
//      if (newTable.schema.length === 0) { // Set headers with the first row
//        for (let headerName of stringRow.split(fieldSeparator)) {
//          let newHeader = new Header(headerName.trim());
//          newTable.schema.push(newHeader);
//        }
//      } else {
//        for (let value of stringRow.split(fieldSeparator)) {
//          let header = newTable.schema[column];
//          let cell = new Cell(header, row, column, value.trim());
//          newTable.cells.push(cell);
//          column++;
//        }
//        row++;
//      }
//    }
//    console.log(newTable);
//    return newTable;
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

  private parseCSV(data: string,
                  options?: {
                            delimiter?: string;   // e.g. ',', ';', '\t', '|'
                            quoteChar?: string;   // e.g. '"'
                            skipEmptyLines?: boolean;
                            trimFields?: boolean;
                            }
                            ): string[][] {
    const delimiter = options?.delimiter ?? this.detectDelimiter(data);
    const quoteChar = options?.quoteChar ?? this.detectQuoteChar(data);
    const skipEmptyLines = options?.skipEmptyLines ?? true;
    const trimFields = options?.trimFields ?? true;

    const rows: string[][] = [];
    let currentRow: string[] = [];
    let currentField = "";

    let insideQuotes = false;

    for (let i = 0; i < data.length; i++) {
      const char = data[i];
      const nextChar = data[i + 1];

      if (char === quoteChar) {
        if (insideQuotes && nextChar === quoteChar) {
          // Escaped quote ("")
          currentField += quoteChar;
          i++;
        } else {
          // Toggle quoted field state
          insideQuotes = !insideQuotes;
        }
      } else if (char === delimiter && !insideQuotes) {
        // End of field
        currentRow.push(trimFields ? currentField.trim() : currentField);
        currentField = "";
      } else if ((char === "\n" || char === "\r") && !insideQuotes) {
        // End of row
        if (currentField.length > 0 || !skipEmptyLines) {
          currentRow.push(trimFields ? currentField.trim() : currentField);
        }
        if (currentRow.length > 0 || !skipEmptyLines) {
          rows.push(currentRow);
        }
        currentRow = [];
        currentField = "";

        // Handle Windows \r\n newlines
        if (char === "\r" && nextChar === "\n") {
          i++;
        }
      } else {
        currentField += char;
      }
    }

    // Push last row if not empty
    if (currentField.length > 0 || currentRow.length > 0) {
      currentRow.push(trimFields ? currentField.trim() : currentField);
      rows.push(currentRow);
    }

    return rows;
  }

  private detectDelimiter(data: string): string {
    const delimiters = [",", ";", "\t", "|"];
    const firstLine = data.split(/\r?\n/)[0];
    let bestDelimiter = ",";
    let maxCount = 0;
    for (const d of delimiters) {
      const count = firstLine.split(d).length;
      if (count > maxCount) {
        maxCount = count;
        bestDelimiter = d;
      }
    }
    return bestDelimiter;
  }

  private detectQuoteChar(data: string): string | undefined {
    const candidates = ['"', "'"];
    const sample = data.split(/\r?\n/).slice(0, 5).join("\n"); // look at first few lines

    for (const q of candidates) {
      const matches = sample.match(new RegExp(`\\${q}`, "g"));
      if (matches && matches.length >= 2) {
        return q;
      }
    }

    return undefined; // no quote char detected
  }

  private generateTable(rows: string[][]): Table {
    let row = 0;
    let newTable = new Table();
    let headers = rows[0]
    for (let csvRow of rows) {
      let column = 0;
      if (newTable.schema.length === 0) {
        for (let headerName of headers) {
          let newHeader = new Header(headerName.trim());
          newTable.schema.push(newHeader);
        }
      } else {
        for (let value of csvRow) {
          let header = newTable.schema[column]
          let cell = new Cell(header, row, column, value.trim());
          newTable.cells.push(cell);
          column++;
        }
        row++;
      }
    }
    return newTable;
  }

}
