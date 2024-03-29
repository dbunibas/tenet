package it.unibas.tenet.model.dto.frontend;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import org.bson.types.ObjectId;

@Data
public class HeaderFrontendDTO {

    @NotBlank
    private String name;
    private String type;

}
