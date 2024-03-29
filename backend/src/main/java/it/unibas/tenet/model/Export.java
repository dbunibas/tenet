package it.unibas.tenet.model;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.quarkus.mongodb.panache.common.MongoEntity;
import java.util.List;
import lombok.Data;
import org.bson.types.ObjectId;

@MongoEntity(collection = "exports")
@Data
public class Export {
    
    private ObjectId id;
    
    private ObjectId projectId;
    
    private String projectName;
    
    private boolean completed = false;
    
    private List<ExportExample> examples; 
    
    public String exampleToJSON() throws JsonProcessingException {
        ObjectMapper objectMapper = new ObjectMapper();
        return objectMapper.writeValueAsString(examples);
    }

}
