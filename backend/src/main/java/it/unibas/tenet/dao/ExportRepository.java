package it.unibas.tenet.dao;

import io.quarkus.mongodb.panache.PanacheMongoRepository;
import it.unibas.tenet.model.Export;
import jakarta.enterprise.context.ApplicationScoped;
import java.util.List;
import org.bson.types.ObjectId;

@ApplicationScoped
public class ExportRepository implements PanacheMongoRepository<Export> {

    public Export findById(String exportId) {
        return this.findById(new ObjectId(exportId));
    }

    public List<Export> findByProjectId(String projectId) {
        return find("projectId", new ObjectId(projectId)).list();
    }

    public List<Export> findCompleted() {
        return find("completed", true).list();
    }

}
