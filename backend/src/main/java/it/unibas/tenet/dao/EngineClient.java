package it.unibas.tenet.dao;

import it.unibas.tenet.model.SemanticQuery;
import it.unibas.tenet.model.dto.engine.ExportExampleEngineDTO;
import it.unibas.tenet.model.dto.engine.GenerateEvidenceEngineDTO;
import it.unibas.tenet.model.dto.engine.GenerateSentencesEngineDTO;
import it.unibas.tenet.model.dto.engine.GeneratedEvidenceDTO;
import it.unibas.tenet.model.dto.engine.LaunchExportEngineDTO;
import it.unibas.tenet.model.dto.engine.ProjectEngineDTO;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.POST;
import jakarta.ws.rs.Path;
import java.util.List;
import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;


@Path("/")
@RegisterRestClient(configKey = "tenet-api")
public interface EngineClient {

    @GET
    @Path("/up")
    String up();

    @POST
    @Path("/evidence/generateSQL")
    String getSQLQuery(ProjectEngineDTO projectData);

    @POST
    @Path("/evidence/generateEvidence")
    GeneratedEvidenceDTO generateEvidence(GenerateEvidenceEngineDTO generationData);

    @POST
    @Path("/evidence/findSemanticQueries")
    public List<SemanticQuery> getSemanticQueries(ProjectEngineDTO projectEngineDTO);
    
    @POST
    @Path("/evidence/generateSentences")
    public List<String> generateSentences(GenerateSentencesEngineDTO sentencesDTO);
    
    @POST
    @Path("/evidence/exportSentences")
    public List<ExportExampleEngineDTO> exportSentences(LaunchExportEngineDTO engineDTO);
}
