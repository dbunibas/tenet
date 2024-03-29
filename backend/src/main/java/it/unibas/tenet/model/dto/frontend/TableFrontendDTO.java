package it.unibas.tenet.model.dto.frontend;

import io.smallrye.common.constraint.NotNull;
import java.util.List;
import lombok.Data;

@Data
public class TableFrontendDTO {

    @NotNull
    private List<HeaderFrontendDTO> schema;
    @NotNull
    private List<CellFrontendDTO> cells;
}
