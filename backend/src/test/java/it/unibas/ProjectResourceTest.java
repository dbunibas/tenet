package it.unibas;

import groovy.util.logging.Slf4j;
import io.quarkus.test.junit.QuarkusTest;
import static io.restassured.RestAssured.given;
import it.unibas.tenet.dao.ProjectRepository;
import it.unibas.tenet.model.dto.frontend.DatabaseFrontendDTO;
import it.unibas.tenet.model.dto.frontend.ProjectFrontendDTO;
import it.unibas.tenet.model.dto.frontend.TableFrontendDTO;
import it.unibas.tenet.service.ProjectService;
import jakarta.inject.Inject;
import java.util.ArrayList;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

@Slf4j
@QuarkusTest
public class ProjectResourceTest {

    private static final String BASE = "/api/v1";

    @Inject
    private ProjectRepository projectRepository;

    @Test
    public void getProjectsTest() {
        given().header("Content-Type", "application/json")
                .when().get(BASE + "/projects")
                .then()
                .statusCode(401);
    }

    @Inject
    private ProjectService projectService;

    @Test
    public void testProjectCreate() {
        ProjectFrontendDTO p1 = new ProjectFrontendDTO();
        DatabaseFrontendDTO dbDTO = new DatabaseFrontendDTO();
        TableFrontendDTO tbDTO = new TableFrontendDTO();
        tbDTO.setCells(new ArrayList<>());
        tbDTO.setSchema(new ArrayList<>());
        dbDTO.setTable(tbDTO);
        p1.setDatabase(dbDTO);
        p1.setName("Mock project");
        ProjectFrontendDTO created = this.projectService.createProject(p1);
        String newId = created.getId().toString();
        Assertions.assertFalse(newId.isEmpty());
        Assertions.assertNotNull(this.projectService.getProjectById(newId));
        projectRepository.deleteById(created.getId());
    }

}
