package it.unibas.tenet.model.dto.frontend;

import io.smallrye.common.constraint.NotNull;
import it.unibas.tenet.model.SemanticQuery;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Positive;
import lombok.Data;

@Data
public class GenerateSentenceFrontendDTO {
    
    @NotBlank
    private SemanticQuery sentenceType;
    @NotNull
    @Positive
    private int number;

}
