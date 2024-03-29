package it.unibas.tenet.rest;

import it.unibas.tenet.model.dto.frontend.ExportFrontendDTO;
import it.unibas.tenet.model.dto.frontend.LaunchExportFrontendDTO;
import it.unibas.tenet.service.ExportService;
import it.unibas.tenet.service.ProjectService;
import jakarta.annotation.security.PermitAll;
import jakarta.enterprise.context.RequestScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import java.util.List;
import lombok.extern.slf4j.Slf4j;
import org.eclipse.microprofile.openapi.annotations.security.SecurityRequirement;

@RequestScoped
@Path("/exports")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
@Slf4j
public class ExportResource {
    
    
    @Inject
    private ProjectService projectService;
    
    @Inject
    private ExportService exportService;

    @POST
    @Path("")
    @Produces(MediaType.TEXT_PLAIN)
    @SecurityRequirement(name = "bearerAuth")
    public String startExport(@PathParam("projectId") String projectId, LaunchExportFrontendDTO exportDTO) {
        return projectService.startExport(projectId, exportDTO);
    }
    
    @GET
    @Path("")
    @SecurityRequirement(name="bearerAuth")
    public List<ExportFrontendDTO> getExports() {
        return exportService.getExports();
    }

    @GET
    @Path("/{exportId}")
    @SecurityRequirement(name = "bearerAuth")
    @Produces(MediaType.TEXT_PLAIN)
    public String getExportData(@PathParam("exportId") String exportId) {
        return exportService.getExportData(exportId);
    }

}
