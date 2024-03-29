package it.unibas.tenet.dao;

import io.quarkus.mongodb.panache.PanacheMongoRepository;
import it.unibas.tenet.model.User;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class UserRepository implements PanacheMongoRepository<User> {

    public User findByUsername(String username) {
        return find("username", username).firstResult();
    }

}
