package it.unibas.tenet.model.dto.engine;

import it.unibas.tenet.model.Evidence;
import it.unibas.tenet.model.SemanticQuery;
import lombok.Data;

@Data
public class GenerateSentencesEngineDTO {
    
    private String name;
    private TableEngineDTO table;
    private Evidence evidence;
    private SemanticQuery sentenceType;
    private int sentenceNumber;

}
