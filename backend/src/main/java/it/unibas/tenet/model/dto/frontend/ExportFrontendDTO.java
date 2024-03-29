package it.unibas.tenet.model.dto.frontend;

import lombok.Data;
import org.bson.types.ObjectId;

@Data
public class ExportFrontendDTO {
    
    private ObjectId id;
    
    private String projectName;
    private int exampleNumber;

}
