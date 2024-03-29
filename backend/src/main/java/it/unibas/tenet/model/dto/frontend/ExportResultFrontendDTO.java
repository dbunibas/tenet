package it.unibas.tenet.model.dto.frontend;

import it.unibas.tenet.model.*;
import java.util.List;
import lombok.Data;

@Data
public class ExportResultFrontendDTO {

    private List<EvidenceFrontendDTO> evidence;
    private List<String> sentences;
    private TableFrontendDTO table;
    private String prompt;
    private SemanticQuery operation;
    private boolean negative;

}
