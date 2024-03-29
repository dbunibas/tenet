package it.unibas.tenet.model.dto.frontend;

import io.smallrye.common.constraint.NotNull;
import jakarta.validation.constraints.PositiveOrZero;
import lombok.Data;

@Data
public class EvidenceToGenerateDTO {

    @NotNull
    @PositiveOrZero
    private Integer positiveNumber;
    @NotNull
    @PositiveOrZero
    private Integer negativeNumber;

}
