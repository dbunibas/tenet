package it.unibas.tenet.model;

import java.util.List;
import lombok.Data;

@Data
public class ExportExample {

    private ExportedEvidence evidence;
    private List<String> sentences;
    private Table table;
    private String prompt;
    private SemanticQuery operation;
    private boolean negative;
    

}
