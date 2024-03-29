package it.unibas.tenet.model;

import io.quarkus.mongodb.panache.common.MongoEntity;
import lombok.Data;
import org.bson.types.ObjectId;

@MongoEntity(collection = "users")
@Data
public class User {

    private ObjectId id;
    private String username;
    private String password;

}
