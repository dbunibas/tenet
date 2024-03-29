package it.unibas.tenet.model.dto.frontend;

import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.PositiveOrZero;
import lombok.Data;

@Data
public class LaunchExportFrontendDTO {
    
    @PositiveOrZero
    private int positiveNumber;
    @PositiveOrZero
    private int negativeNumber;
    @Positive
    private int sentencesNumber;

}
