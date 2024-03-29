package it.unibas.tenet.model;

import lombok.Data;

@Data
public class Database {

    private Table table;
    
    private Table negativeTable;

}
