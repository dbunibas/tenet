package it.unibas.tenet.model.dto.engine;

import it.unibas.tenet.model.*;
import java.util.List;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class ExportExampleEngineDTO {

    private Evidence evidence;
    private List<String> sentences;
    private TableEngineDTO table;
    private String prompt;
    private SemanticQuery operation;
    private boolean negative;

}
