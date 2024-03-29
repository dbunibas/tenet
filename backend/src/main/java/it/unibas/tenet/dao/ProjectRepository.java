package it.unibas.tenet.dao;

import io.quarkus.mongodb.panache.PanacheMongoRepository;
import it.unibas.tenet.model.Project;
import jakarta.enterprise.context.ApplicationScoped;
import org.bson.types.ObjectId;

@ApplicationScoped
public class ProjectRepository implements PanacheMongoRepository<Project> {

    public Project findById(String projectId) {
        return this.findById(new ObjectId(projectId));
    }

//    public Project findByName(String name) {
//        PanacheQuery<Project> projects = this.find("name", name);
//        return projects.firstResult();
//    }
    public Project findByName(String name) {
        return streamAll().filter(p -> p.getName().equalsIgnoreCase(name)).findFirst().orElse(null);
    }

}
