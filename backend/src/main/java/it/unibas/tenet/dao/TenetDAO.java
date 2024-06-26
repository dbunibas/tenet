package it.unibas.tenet.dao;

import it.unibas.tenet.model.Evidence;
import it.unibas.tenet.model.ExportExample;
import it.unibas.tenet.model.ExportedEvidence;
import it.unibas.tenet.model.Project;
import it.unibas.tenet.model.Table;
import it.unibas.tenet.model.SemanticQuery;
import it.unibas.tenet.model.dto.engine.ExportExampleEngineDTO;
import it.unibas.tenet.model.dto.engine.GenerateEvidenceEngineDTO;
import it.unibas.tenet.model.dto.engine.GenerateSentencesEngineDTO;
import it.unibas.tenet.model.dto.engine.GeneratedEvidenceDTO;
import it.unibas.tenet.model.dto.engine.LaunchExportEngineDTO;
import it.unibas.tenet.model.dto.engine.ProjectEngineDTO;
import it.unibas.tenet.model.dto.engine.TableEngineDTO;
import it.unibas.tenet.util.Mapper;
import jakarta.enterprise.context.ApplicationScoped;
import java.util.ArrayList;
import java.util.List;
import lombok.extern.slf4j.Slf4j;
import org.bson.types.ObjectId;
import org.eclipse.microprofile.rest.client.inject.RestClient;

@ApplicationScoped
@Slf4j
public class TenetDAO {

    @RestClient
    EngineClient client;

    public boolean isUp() {
        return client.up().equalsIgnoreCase("server is up");
    }

    public String getSQLQuery(String projectName, Table table, Evidence evidence) {
        ProjectEngineDTO projectEngineDTO = new ProjectEngineDTO(projectName);
        TableEngineDTO tableEngineDTO = Mapper.map(table, TableEngineDTO.class);
        tableEngineDTO.setHeaders(table.getSchema());
        projectEngineDTO.setTable(tableEngineDTO);
        projectEngineDTO.setUserEvidence(evidence);
        return client.getSQLQuery(projectEngineDTO);
    }

    public GeneratedEvidenceDTO generateEvidence(Project project, Integer nPositives, Integer nNegatives) {
        if (nPositives < 0 || nNegatives < 0) {
            throw new IllegalArgumentException("Can't generate negative numbers");
        }
        GenerateEvidenceEngineDTO generateData = new GenerateEvidenceEngineDTO();
        generateData.setName(project.getName());
        generateData.setPositiveNumber(nPositives);
        generateData.setNegativeNumber(nNegatives);
        TableEngineDTO tableDTO = Mapper.map(project.getDatabase().getTable(), TableEngineDTO.class);
        tableDTO.setHeaders(project.getDatabase().getTable().getSchema());
        generateData.setTable(tableDTO);
        generateData.setUserEvidence(project.findUserEvidence());
        if (project.getDatabase().getNegativeTable() != null) {
            TableEngineDTO negativeTable = Mapper.map(project.getDatabase().getNegativeTable(), TableEngineDTO.class);
            negativeTable.setHeaders(project.getDatabase().getNegativeTable().getSchema());
            generateData.setNegativeTable(negativeTable);
        }
        GeneratedEvidenceDTO data = client.generateEvidence(generateData);

        for (Evidence evidence : data.getEvidence()) {
            evidence.setId(new ObjectId());
            evidence.setAutoGenerated(true);
        }

        return data;
    }

    public List<SemanticQuery> getSemanticQueries(String projectName, Table table, Evidence evidence) {
        ProjectEngineDTO projectEngineDTO = new ProjectEngineDTO(projectName);
        TableEngineDTO tableEngineDTO = Mapper.map(table, TableEngineDTO.class);
        tableEngineDTO.setHeaders(table.getSchema());
        projectEngineDTO.setTable(tableEngineDTO);
        projectEngineDTO.setUserEvidence(evidence);
        return client.getSemanticQueries(projectEngineDTO);
    }

    public List<String> generateSentences(String projectName, Table table, Evidence evidence, SemanticQuery sentenceType, int number) {
        if (number < 1) {
            throw new IllegalArgumentException("Number not valid");
        }
        GenerateSentencesEngineDTO generateDTO = new GenerateSentencesEngineDTO();
        generateDTO.setName(projectName);
        generateDTO.setTable(Mapper.map(table, TableEngineDTO.class));
        generateDTO.getTable().setHeaders(table.getSchema());
        generateDTO.setEvidence(evidence);
        generateDTO.setSentenceNumber(number);
        generateDTO.setSentenceType(sentenceType);
        List<String> sentences = client.generateSentences(generateDTO);
        return sentences;
    }

    public List<ExportExample> exportSentences(String projectName, Table table, Evidence evidence, int positiveNumber, int negativeNumber, int sentencesNumber) {
        TableEngineDTO tableEngineDTO = Mapper.map(table, TableEngineDTO.class);
        tableEngineDTO.setHeaders(table.getSchema());
        LaunchExportEngineDTO engineDTOData = new LaunchExportEngineDTO();
        engineDTOData.setName(projectName);
        engineDTOData.setTable(tableEngineDTO);
        engineDTOData.setUserEvidence(evidence);
        engineDTOData.setPositiveNumber(positiveNumber);
        engineDTOData.setNegativeNumber(negativeNumber);
        engineDTOData.setSentencesNumber(sentencesNumber);
        log.debug("OK2 ");
        List<ExportExampleEngineDTO> exportResultDTO = client.exportSentences(engineDTOData);

        List<ExportExample> resultList = new ArrayList<>();
        for (ExportExampleEngineDTO resultDTO : exportResultDTO) {
            ExportExample result = Mapper.map(resultDTO, ExportExample.class);
            Table t = Mapper.map(resultDTO.getTable(), Table.class);
            t.setSchema(resultDTO.getTable().getHeaders());
            result.setTable(t);
            result.setEvidence(Mapper.map(resultDTO.getEvidence(), ExportedEvidence.class));
            resultList.add(result);
        }
        log.debug("RESULT: " + resultList);
        return resultList;
    }

}
