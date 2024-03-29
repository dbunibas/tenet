import {Header} from "./header";

export class Cell {
  constructor(
    public header: Header,
    public row: number,
    public column: number,
    public value: any
  ) {
  }
  public selected: boolean = false;
}
