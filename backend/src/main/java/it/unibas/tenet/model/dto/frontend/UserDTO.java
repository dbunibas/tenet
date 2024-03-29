package it.unibas.tenet.model.dto.frontend;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;
import org.bson.types.ObjectId;

@Data
public class UserDTO {

    private ObjectId id;
    @NotBlank(message = "Provide username")
    private String username;
    @NotBlank(message = "Provide password")
    private String password;

    private String authToken;
}
