package it.unibas.tenet.model.dto.frontend;

import io.smallrye.common.constraint.NotNull;
import it.unibas.tenet.model.Table;
import lombok.Data;

@Data
public class DatabaseFrontendDTO {

    @NotNull
    private TableFrontendDTO table;
    
    private Table negativeTable;

}
