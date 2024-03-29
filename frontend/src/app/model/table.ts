import {Cell} from "./cell";
import {Header} from "./header";

export class Table {

  public cells: Cell[] = [];
  public schema: Header[] = [];

  public rows: any[] = [];
}
