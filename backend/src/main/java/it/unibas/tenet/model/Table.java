package it.unibas.tenet.model;

import java.util.List;
import lombok.Data;

@Data
public class Table {

    private List<Header> schema;

    private List<Cell> cells;


}
