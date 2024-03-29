package it.unibas.tenet.model.dto.frontend;

import io.smallrye.common.constraint.NotNull;
import jakarta.validation.constraints.PositiveOrZero;
import lombok.Data;

@Data
public class CellFrontendDTO {

    @NotNull
    private HeaderFrontendDTO header;
    @NotNull
    @PositiveOrZero
    private int column;
    @NotNull
    @PositiveOrZero
    private int row;
    @NotNull
    private String value;

}
