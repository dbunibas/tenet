package it.unibas.tenet.model.dto.engine;

import it.unibas.tenet.model.Evidence;
import lombok.Data;

@Data
public class LaunchExportEngineDTO {
    
    private String name;
    private TableEngineDTO table;
    private Evidence userEvidence;
    private int positiveNumber;
    private int negativeNumber;
    private int sentencesNumber;

}
