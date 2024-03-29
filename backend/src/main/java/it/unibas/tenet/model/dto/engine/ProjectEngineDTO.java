package it.unibas.tenet.model.dto.engine;

import it.unibas.tenet.model.Evidence;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
public class ProjectEngineDTO {

    public ProjectEngineDTO(String name) {
        this.name = name;
    }

    private String name;

    private TableEngineDTO table;

    private Evidence userEvidence;

}
