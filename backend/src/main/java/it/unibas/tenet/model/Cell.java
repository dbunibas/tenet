package it.unibas.tenet.model;

import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class Cell {

    private Header header;
    private int column;
    private int row;
    private String value;

    public Cell(Header header, String value, int row, int column) {
        this.header = header;
        this.column = column;
        this.row = row;
        this.value = value;
    }
    
    

}
