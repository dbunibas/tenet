package it.unibas.tenet.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import io.smallrye.mutiny.Uni;
import io.smallrye.mutiny.infrastructure.Infrastructure;
import it.unibas.tenet.dao.ExportRepository;
import it.unibas.tenet.dao.ProjectRepository;
import it.unibas.tenet.dao.TenetDAO;
import it.unibas.tenet.filter.exceptions.NotFoundException;
import it.unibas.tenet.model.Evidence;
import it.unibas.tenet.model.Export;
import it.unibas.tenet.model.Project;
import it.unibas.tenet.model.SemanticQuery;
import it.unibas.tenet.model.Table;
import it.unibas.tenet.model.dto.engine.GeneratedEvidenceDTO;
import it.unibas.tenet.model.dto.frontend.EvidenceFrontendDTO;
import it.unibas.tenet.model.dto.frontend.EvidenceToGenerateDTO;
import it.unibas.tenet.model.dto.frontend.ExportResultFrontendDTO;
import it.unibas.tenet.model.dto.frontend.GenerateSentenceFrontendDTO;
import it.unibas.tenet.model.dto.frontend.LaunchExportFrontendDTO;
import it.unibas.tenet.model.dto.frontend.ProjectFrontendDTO;
import it.unibas.tenet.model.dto.frontend.QueryFrontendDTO;
import it.unibas.tenet.util.Mapper;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;
import java.util.logging.Level;
import java.util.logging.Logger;
import lombok.extern.slf4j.Slf4j;
import org.bson.types.ObjectId;

@ApplicationScoped
@Slf4j
public class ProjectService {

    @Inject
    private ProjectRepository projectRepository;

    @Inject
    private TenetDAO tenetDAO;

    public List<ProjectFrontendDTO> getAll() {
        List<Project> projects = projectRepository.listAll();
        List<ProjectFrontendDTO> dtoProjects = new ArrayList<>();
        for (Project project : projects) {
            ProjectFrontendDTO dtoProject = new ProjectFrontendDTO();
            dtoProject.setId(project.getId());
            dtoProject.setName(project.getName());
            dtoProjects.add(dtoProject);
        }
        log.debug("Loaded {} projects", dtoProjects.size());
        return dtoProjects;
    }

    public ProjectFrontendDTO createProject(ProjectFrontendDTO projectDTO) {
        if (projectRepository.findByName(projectDTO.getName()) != null) {
            throw new IllegalArgumentException("Project with name " + projectDTO.getName() + " already exist");
        }
        Project newProject = Mapper.map(projectDTO, Project.class);
        log.debug("Deserialized project {}", newProject);
        projectRepository.persist(newProject);
        log.debug("Created project {}", newProject.getId());
        projectDTO.setDatabase(null);
        projectDTO.setId(newProject.getId());
        return projectDTO;
    }

    private Project getProjectByIdOrThrow(String projectId) {
        Project project = projectRepository.findById(projectId);
        if (project == null) {
            log.error("Project with id {} not found", projectId);
            throw new NotFoundException("Project not found");
        }
        return project;
    }

    public ProjectFrontendDTO getProjectById(String projectId) {
        Project project = getProjectByIdOrThrow(projectId);
        log.debug("Opening project {}: \"{}\"", projectId, project.getName());
        return Mapper.map(project, ProjectFrontendDTO.class);
    }

    public List<EvidenceFrontendDTO> getEvidence(String projectId) {
        Project project = getProjectByIdOrThrow(projectId);
        List<Evidence> evidence = project.getEvidence();
        return Mapper.map(evidence, EvidenceFrontendDTO.class);
    }

    public EvidenceFrontendDTO createEvidence(EvidenceFrontendDTO evidenceDTO, String projectId) {
        Project project = getProjectByIdOrThrow(projectId);
        Evidence newEvidence = Mapper.map(evidenceDTO, Evidence.class);
        newEvidence.setId(new ObjectId());
        if (project.getEvidence() == null) {
            project.setEvidence(new ArrayList<>());
        }
        Evidence existingEvidence = project.findUserEvidence();
        if (existingEvidence != null) {
            throw new IllegalArgumentException("User generated evidence already set");
        }
        project.getEvidence().add(newEvidence);
        log.debug("Evidence list: {}", project.getEvidence());
        projectRepository.persistOrUpdate(project);
        log.debug("Saved evidence with id {}", newEvidence.getId());
        return Mapper.map(newEvidence, EvidenceFrontendDTO.class);
    }

    public void updateUserEvidence(EvidenceFrontendDTO evidenceDTO, String projectId, String evidenceId) {
        Project project = getProjectByIdOrThrow(projectId);
        if (!evidenceDTO.getId().toString().equals(evidenceId)) {
            log.debug("Evidence: {} \n New: {}", evidenceDTO.getId(), evidenceId);
            throw new IllegalArgumentException("Uncostistence in id");
        }
        Evidence evidence = project.findEvidenceById(evidenceId);
        if (evidence == null) {
            throw new IllegalArgumentException("Invalid evidence id");
        }
        project.resetProject();
        Evidence newEvidence = Mapper.map(evidenceDTO, Evidence.class);
        newEvidence.setId(new ObjectId());
        project.getEvidence().add(newEvidence);
        newEvidence.getSentences().clear();
        newEvidence.getSemanticQueries().clear();
        projectRepository.persistOrUpdate(project);
    }

    public QueryFrontendDTO getSQLQuery(String projectId) {
        Project project = getProjectByIdOrThrow(projectId);
        Evidence userEvidence = project.findUserEvidence();
        if (userEvidence == null) {
            throw new IllegalArgumentException("No user evidence found");
        }
        if (project.getQuery() != null) {
            return new QueryFrontendDTO(project.getQuery());
        }
        String sql = tenetDAO.getSQLQuery(project.getName(), project.getDatabase().getTable(), userEvidence);
        sql = sql.substring(1, sql.length() - 1);
        project.setQuery(sql);
        projectRepository.persistOrUpdate(project);
        return new QueryFrontendDTO(sql);
    }

    public List<EvidenceFrontendDTO> generateEvidence(String projectId, EvidenceToGenerateDTO evidenceToGenerate) {
        Project project = getProjectByIdOrThrow(projectId);
        if (project.findUserEvidence() == null) {
            throw new IllegalArgumentException("No user evidence found");
        }
        log.debug("Requested generation: {} positive, {} negative", evidenceToGenerate.getPositiveNumber(), evidenceToGenerate.getNegativeNumber());
        GeneratedEvidenceDTO generatedEvidence = tenetDAO.generateEvidence(project, evidenceToGenerate.getPositiveNumber(), evidenceToGenerate.getNegativeNumber());
        project.getEvidence().addAll(generatedEvidence.getEvidence());
        Table negativeTable = Mapper.map(generatedEvidence.getNegativeTable(), Table.class);
        negativeTable.setSchema(generatedEvidence.getNegativeTable().getHeaders());
        project.getDatabase().setNegativeTable(negativeTable);
        projectRepository.persistOrUpdate(project);
        log.debug("Generated evidence: {}", generatedEvidence);
        return Mapper.map(generatedEvidence.getEvidence(), EvidenceFrontendDTO.class);
    }

    public List<SemanticQuery> getSemanticQueries(String projectId, String evidenceId) {
        Project project = getProjectByIdOrThrow(projectId);
        Evidence evidence = project.findEvidenceById(evidenceId);
        if (evidence == null) {
            throw new NotFoundException("Evidence not found");
        }
        Table table = evidence.isNegative() ? project.getDatabase().getNegativeTable() : project.getDatabase().getTable();
        List<SemanticQuery> semanticQueries = tenetDAO.getSemanticQueries(project.getName(), table, evidence);
        evidence.setSemanticQueries(semanticQueries);
        projectRepository.persistOrUpdate(project);
        log.debug("Return {} semantic queries for evidence {}", semanticQueries.size(), evidence.getId());
        return semanticQueries;
    }

    public List<String> generateSentences(String projectId, String evidenceId, GenerateSentenceFrontendDTO generateSentenceDTO) {
        Project project = getProjectByIdOrThrow(projectId);
        Evidence evidence = project.findEvidenceById(evidenceId);
        if (evidence == null) {
            throw new NotFoundException("Evidence not found");
        }
        SemanticQuery sentenceType = generateSentenceDTO.getSentenceType();
        if (evidence.getSemanticQueries().isEmpty() || !evidence.getSemanticQueries().contains(sentenceType)) {
            throw new IllegalArgumentException("Sentence Type not found");
        }
        int number = generateSentenceDTO.getNumber();
        Table table = evidence.isNegative() ? project.getDatabase().getNegativeTable() : project.getDatabase().getTable();
        List<String> sentences = tenetDAO.generateSentences(project.getName(), table, evidence, sentenceType, number);
        evidence.setSentences(sentences);
        projectRepository.persistOrUpdate(project);
        log.debug("Generated {} sentences for evidence {}", sentences.size(), evidence.getId());
        return sentences;
    }

    @Inject
    private ExportService exportService;
    
    @Inject
    private ExportRepository exportRepository;

    public String startExport(String projectId, LaunchExportFrontendDTO exportDTO) {
        Project project = this.getProjectByIdOrThrow(projectId);
        Evidence userEvidence = project.findUserEvidence();
        if (userEvidence == null) {
            throw new NotFoundException("No user evidence for the project");
        }
        int positiveNumber = exportDTO.getPositiveNumber();
        int negativeNumber = exportDTO.getNegativeNumber();
        int sentencesNumber = exportDTO.getSentencesNumber();
        
        Export newExport = new Export();
        newExport.setProjectId(project.getId());
        newExport.setProjectName(project.getName());
        exportRepository.persist(newExport);
        
//        Uni.createFrom().voidItem().invoke(() -> {
//            log.debug("Starting exports");
//            exportService.startExport(newExport.getId().toString(), project, userEvidence, positiveNumber, negativeNumber, sentencesNumber);
//        }).emitOn(runnable -> {}).subscribe().with(
//                item -> log.debug("Finished exports")
//        );

        Uni.createFrom().voidItem().invoke(() -> {
            log.debug("Starting exports");
            exportService.startExport(newExport.getId().toString(), project, userEvidence, positiveNumber, negativeNumber, sentencesNumber);
        }).runSubscriptionOn(Infrastructure.getDefaultWorkerPool())
                .subscribeAsCompletionStage()
                .whenComplete((i, e) -> {
                    if(e != null) {
                        log.error(e.getLocalizedMessage());
                    }
                });
        log.debug("Export started");
        return newExport.getId().toString();
    }

}
