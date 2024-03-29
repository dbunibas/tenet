package it.unibas.tenet.rest;

import io.smallrye.common.constraint.NotNull;
import it.unibas.tenet.model.dto.frontend.EvidenceFrontendDTO;
import it.unibas.tenet.model.dto.frontend.EvidenceToGenerateDTO;
import it.unibas.tenet.model.dto.frontend.ProjectFrontendDTO;
import it.unibas.tenet.model.dto.frontend.QueryFrontendDTO;
import it.unibas.tenet.service.ProjectService;
import jakarta.annotation.security.PermitAll;
import jakarta.enterprise.context.RequestScoped;
import jakarta.inject.Inject;
import jakarta.validation.Valid;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.PUT;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import java.util.List;
import lombok.extern.slf4j.Slf4j;
import org.eclipse.microprofile.openapi.annotations.security.SecurityRequirement;
import org.eclipse.microprofile.rest.client.inject.RestClient;
import it.unibas.tenet.dao.EngineClient;
import it.unibas.tenet.model.SemanticQuery;
import it.unibas.tenet.model.dto.frontend.ExportResultFrontendDTO;
import it.unibas.tenet.model.dto.frontend.GenerateSentenceFrontendDTO;
import it.unibas.tenet.model.dto.frontend.LaunchExportFrontendDTO;
import it.unibas.tenet.service.ExportService;

@RequestScoped
@Path("/projects")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@Slf4j
public class ProjectResource {

    @Inject
    private ProjectService projectService;
    
    @GET
    @SecurityRequirement(name = "bearerAuth")
    public List<ProjectFrontendDTO> getAll() {
        return projectService.getAll();
    }

    @GET
    @SecurityRequirement(name = "bearerAuth")
    @Path("/{projectId}")
    public ProjectFrontendDTO getProject(@NotNull @PathParam("projectId") String projectId) {
        return this.projectService.getProjectById(projectId);
    }

    @POST
    @SecurityRequirement(name = "bearerAuth")
    public ProjectFrontendDTO createProject(@NotNull @Valid ProjectFrontendDTO projectDTO) {
        return projectService.createProject(projectDTO);
    }

    @GET
    @Path("/{projectId}/evidence")
    @SecurityRequirement(name = "bearerAuth")
    public List<EvidenceFrontendDTO> getEvidences(@PathParam("projectId") String projectId) {
        return this.projectService.getEvidence(projectId);
    }

    @POST
    @Path("/{projectId}/evidence")
    @SecurityRequirement(name = "bearerAuth")
    public EvidenceFrontendDTO createEvidence(@NotNull @Valid EvidenceFrontendDTO evidenceDTO, @PathParam("projectId") String projectId) {
        return this.projectService.createEvidence(evidenceDTO, projectId);
    }

    @PUT
    @Path("/{projectId}/evidence/{evidenceId}")
    @SecurityRequirement(name = "bearerAuth")
    public void updateEvidence(@NotNull @Valid EvidenceFrontendDTO evidenceDTO, @PathParam("projectId") String projectId, @PathParam("evidenceId") String evidenceId) {
        this.projectService.updateUserEvidence(evidenceDTO, projectId, evidenceId);;
    }

    @GET
    @Path("/{projectId}/evidence/sql")
    @SecurityRequirement(name = "bearerAuth")
    public QueryFrontendDTO getSQLQuery(@PathParam("projectId") String projectId) {
        return this.projectService.getSQLQuery(projectId);
    }

    @POST
    @Path("/{projectId}/evidence/newEvidence")
    @SecurityRequirement(name = "bearerAuth")
    public List<EvidenceFrontendDTO> generateEvidence(@NotNull @Valid EvidenceToGenerateDTO evidenceToGenerate, @PathParam("projectId") String projectId) {
        return projectService.generateEvidence(projectId, evidenceToGenerate);
    }

    @GET
    @Path("/{projectId}/evidence/{evidenceId}/semanticQueries")
    @SecurityRequirement(name = "bearerAuth")
    public List<SemanticQuery> getSemanticQueries(@PathParam("projectId") String projectId, @PathParam("evidenceId") String evidenceId) {
        return projectService.getSemanticQueries(projectId, evidenceId);
    }

    @POST
    @Path("/{projectId}/evidence/{evidenceId}/sentences")
    @SecurityRequirement(name = "bearerAuth")
    public List<String> generateSentences(@PathParam("projectId") String projectId,
            @PathParam("evidenceId") String evidenceId,
            GenerateSentenceFrontendDTO generateSentenceDTO) {
        return projectService.generateSentences(projectId, evidenceId, generateSentenceDTO);
    }

    @POST
    @Path("/{projectId}/exports")
    @Produces(MediaType.TEXT_PLAIN)
    @SecurityRequirement(name = "bearerAuth")
    public String startExport(@PathParam("projectId") String projectId, LaunchExportFrontendDTO exportDTO) {
        return projectService.startExport(projectId, exportDTO);
    }
    

    @RestClient
    EngineClient client;

    @GET
    @Path("clientTest")
    @PermitAll
    public String testClient() {
        return client.up();
    }
}
