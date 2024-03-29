package it.unibas.tenet.model.dto.engine;

import it.unibas.tenet.model.Evidence;
import java.util.List;
import lombok.Data;

@Data
public class GeneratedEvidenceDTO {

    private List<Evidence> evidence;
    private TableEngineDTO negativeTable;
}
