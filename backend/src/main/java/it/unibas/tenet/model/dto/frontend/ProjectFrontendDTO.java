package it.unibas.tenet.model.dto.frontend;

import io.smallrye.common.constraint.NotNull;
import jakarta.validation.constraints.NotBlank;
import java.util.List;
import lombok.Data;
import org.bson.types.ObjectId;

@Data
public class ProjectFrontendDTO {

    private ObjectId id;

    private List<EvidenceFrontendDTO> evidence;

    @NotBlank
    private String name;

    // private ObjectId userId; 
    @NotNull
    private DatabaseFrontendDTO database;

}
