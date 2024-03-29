package it.unibas.tenet.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import it.unibas.tenet.dao.ExportRepository;
import it.unibas.tenet.dao.ProjectRepository;
import it.unibas.tenet.dao.TenetDAO;
import it.unibas.tenet.filter.exceptions.NotFoundException;
import it.unibas.tenet.model.Evidence;
import it.unibas.tenet.model.Export;
import it.unibas.tenet.model.ExportExample;
import it.unibas.tenet.model.Project;
import it.unibas.tenet.model.Table;
import it.unibas.tenet.model.dto.frontend.ExportFrontendDTO;
import it.unibas.tenet.util.Mapper;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import java.util.ArrayList;
import java.util.List;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@ApplicationScoped
public class ExportService {

    @Inject
    private ExportRepository exportRepository;

    @Inject
    private ProjectRepository projectRepository;

    @Inject
    private TenetDAO tenetDAO;

    public List<ExportFrontendDTO> getExports() {
        List<Export> exports = exportRepository.findCompleted();
        log.debug("{} exports found", exports.size());
        List<ExportFrontendDTO> results = new ArrayList<>();
        for (Export export : exports) {
            ExportFrontendDTO exportDTO = Mapper.map(export, ExportFrontendDTO.class);
            exportDTO.setExampleNumber(export.getExamples().size());
            results.add(exportDTO);
        }
        return results;
    }

    public String getExportData(String exportId) {
        Export export = this.exportRepository.findById(exportId);
        if (export == null) {
            throw new NotFoundException("No export active with the specified id");
        }

        log.debug("Checking status export {}", exportId);
        if (export.isCompleted()) {
            try {
                return export.exampleToJSON();
            } catch (JsonProcessingException ex) {
                throw new IllegalArgumentException("Error in data generation");
            }
        }
        return null;
    }

    public void startExport(String exportId, Project project, Evidence userEvidence, int positiveNumber, int negativeNumber, int sentencesNumber) {
        log.debug("Exporting...");
        String projectName = project.getName();
        Table table = project.getDatabase().getTable();
        List<ExportExample> result;
        Export export = this.exportRepository.findById(exportId);
        try {
            result = tenetDAO.exportSentences(projectName, table, userEvidence, positiveNumber, negativeNumber, sentencesNumber);
        } catch (Exception e) {
            exportRepository.delete(export);
            log.error("EXPORT id {} FAILED: {}", exportId, e);
            return;
        }
        export.setExamples(result);
        export.setCompleted(true);
        exportRepository.persistOrUpdate(export);
        log.info("Export completed {}", exportId);
    }

}
