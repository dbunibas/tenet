from src.Tenet import Tenet
from src.api.ConfigSingleton import ConfigSingleton
from src.api.model.DTO import ExportRequestDTO, ExportSentencesDTO, GeneratedEvidenceDTO, SemanticQueryDTO, \
    SentenceToGenerateDTO
from src.model.OperatorFinder import OperatorFinder
from src.model.RefuteInstancesGenerator import RefuteInstancesGenerator
from src.api.services.DTOMapper import Mapper
from src.model.WarmSearch import WarmSearch
from src.api.model.DTO import EvidenceDTO, EvidenceToGenerateDTO, TableEvidenceDTO
from src.model.RelationalTable import Database, Table, Evidence
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

mapper = Mapper()


class TenetService:
    def __init__(self) -> None:
        # Load config
        config = ConfigSingleton()
        self.disableLanguageModel = False
        self.seed = config.SEED
        self.addRows = config.NEGATIVE_TABLE_GENERATION_ADD_ROWS
        self.rowsToAdd = config.NEGATIVE_TABLE_GENERATION_ROWS_TO_ADD
        self.removeRows = config.NEGATIVE_TABLE_GENERATION_REMOVE_ROWS
        self.rowsToRemove = config.NEGATIVE_TABLE_GENERATION_ROWS_TO_REMOVE
        self.generationStrategy = config.NEGATIVE_TABLE_GENERATION_STRATEGY
        self.operations = config.SENTENCE_GENERATION_OPERATIONS
        self.comparisons = config.SENTENCE_GENERATION_COMPARISONS
        self.bestEvidences = config.CONFIG_TENET_BEST_EVIDENCES
        self.languageModel = config.CONFIG_TENET_LANGUAGE_MODEL
        self.rateLimit = config.CONFIG_TENET_RATE_LIMIT
        self.sleepTime = config.CONFIG_TENET_SLEEP_TIME
        self.address = config.CONFIG_TENET_ADDRESS
        self.numThread = config.CONFIG_TENET_NUM_THREAD

    def generateSQL(self, tableEvidenceDTO: TableEvidenceDTO) -> str:
        table = mapper.tableFromDTOMapper(tableEvidenceDTO.table, tableEvidenceDTO.name)
        database = Database(tableEvidenceDTO.name)
        database.addTable(table)
        database.inferTypes()
        evidence = mapper.evidenceFromDTOMapper(tableEvidenceDTO.userEvidence, tableEvidenceDTO.name)
        query, attrMapping = self._generateQuery(table, evidence)
        log.debug("GENERATED query: " + query)
        return query

    def generateEvidence(self, evidenceToGenerateDTO: EvidenceToGenerateDTO) -> GeneratedEvidenceDTO:
        nPositives = evidenceToGenerateDTO.positiveNumber
        nNegatives = evidenceToGenerateDTO.negativeNumber
        if nPositives < 0 or nNegatives < 0:
            raise ValueError("Number of items to generate not valid")
        tableName = evidenceToGenerateDTO.name
        logging.debug("-- DTO Table:\n" + str(evidenceToGenerateDTO.table))
        table = mapper.tableFromDTOMapper(evidenceToGenerateDTO.table, tableName)
        tableForType = mapper.tableFromDTOMapper(evidenceToGenerateDTO.table, tableName)
        database = Database(tableName)
        database.addTable(tableForType)
        database.inferTypes()
        self._copyTypes(tableForType, table)
        userEvidence = mapper.evidenceFromDTOMapper(evidenceToGenerateDTO.userEvidence, tableName)
        log.debug("-- Original table:\n" + str(table))
        if evidenceToGenerateDTO.negativeTable is None:
            log.debug("Creating negative table")
            negativeTable = self._generateNegativeTable(table, userEvidence)
        else:
            log.debug("Negative table already exist")
            negativeTable = mapper.tableFromDTOMapper(evidenceToGenerateDTO.negativeTable, tableName)
        log.debug("-- Using negative table: \n" + str(negativeTable))
        positiveEvidence, positiveQuery, positiveAttrMapping = self._generateEvidence(table, nPositives, userEvidence)
        log.debug("-- Generated positive evidence: \n" + str(positiveEvidence))
        # negativeEvidence = self._generateEvidence(negativeTable, nNegatives, userEvidence)
        negativeEvidence = self._generateNegativeEvidence(negativeTable, nNegatives, userEvidence, positiveQuery,
                                                          positiveAttrMapping)
        # originalNegativeEvidence = self._getOriginalEvidenceFromNegative(negativeEvidence, table)
        log.debug("-- Generated negative evidence:\n " + str(negativeEvidence))
        # log.debug("-- Generated negative evidence from Original:\n " + str(originalNegativeEvidence))
        generatedEvidence = []
        for evidence in positiveEvidence:
            generatedEvidence.append(mapper.evidenceToDTOMapper(evidence))
        for evidence in negativeEvidence:
            generatedEvidence.append(mapper.evidenceToDTOMapper(evidence, negative=True))
        response = GeneratedEvidenceDTO(
            evidence=generatedEvidence,
            negativeTable=mapper.tableToDTOMapper(negativeTable)
        )
        return response

    def findSemanticQueries(self, tableEvidenceDTO: TableEvidenceDTO) -> list[SemanticQueryDTO]:
        table = mapper.tableFromDTOMapper(tableEvidenceDTO.table, tableEvidenceDTO.name)
        database = Database(tableEvidenceDTO.name)
        database.addTable(table)
        database.inferTypes()
        evidence = mapper.evidenceFromDTOMapper(tableEvidenceDTO.userEvidence, tableEvidenceDTO.name)
        evidence.inferTypesFromDB(database)
        return self._findSemanticQueries(database, evidence)

    def generateSentences(self, generateDTO: SentenceToGenerateDTO) -> list[str]:
        table = mapper.tableFromDTOMapper(generateDTO.table,
                                          generateDTO.name)  # TODO: Check if table should be negativeTable in negative evidence
        database = Database(generateDTO.name)
        database.addTable(table)
        database.inferTypes()
        evidence = mapper.evidenceFromDTOMapper(generateDTO.evidence, generateDTO.name)
        log.debug("SENTENCE TYPE: %s", generateDTO.sentenceType)
        sentenceType = generateDTO.sentenceType.query
        sentenceNumber = generateDTO.sentenceNumber
        sentences = self._generateSentences(database, evidence, sentenceType, sentenceNumber)
        log.debug("Generated %d sentences: ", len(sentences))
        for sentence in sentences:
            log.debug(sentence)
        log.debug("---")
        return sentences

    def exportExamples(self, exportRequestDTO: ExportRequestDTO) -> list[ExportSentencesDTO]:
        # time.sleep(10)
        table = mapper.tableFromDTOMapper(exportRequestDTO.table, exportRequestDTO.name)
        database = Database(exportRequestDTO.name)
        database.addTable(table)
        database.inferTypes()
        userEvidence = mapper.evidenceFromDTOMapper(exportRequestDTO.userEvidence, exportRequestDTO.name)
        return self._batchExampleGeneration(exportRequestDTO.name, table, userEvidence,
                                            exportRequestDTO.positiveNumber, exportRequestDTO.negativeNumber,
                                            exportRequestDTO.sentencesNumber)

    def _generateEvidence(self, table: Table, number: int, evidence: Evidence) -> (list[Evidence], str, dict):
        if number < 0:
            raise ValueError("Invalid number")
        if number == 0:
            return []
        warmSearch = WarmSearch()
        warmSearch.setSeed(self.seed)
        return warmSearch.findEvidences(table, number, evidence)

    def _generateNegativeEvidence(self, table: Table, number: int, evidence: Evidence, query: str, attrMapping: dict) -> \
    list[Evidence]:
        warmSearch = WarmSearch()
        warmSearch.setSeed(self.seed)
        evidences = warmSearch.executeQuery(query, table, attrMapping, number, evidence, shuffle=True)
        return evidences

    def _getOriginalEvidenceFromNegative(self, negativeEvidence, table):
        # originalEvidences = []
        originalEvidence = Evidence(table.tableName)
        for rowEvidence in negativeEvidence.rows:
            rowOriginal = []
            for cellEvidence in rowEvidence:
                rowPos = cellEvidence.getRowPos()
                columnPos = cellEvidence.getColumnPos()
                log.debug("row pos: " + str(rowPos))
                log.debug("Rows in table: " + str(table.getRowNumber()))
                if (rowPos <= table.getRowNumber()):
                    originalCell = table.getCellByPos(rowPos, columnPos)
                    rowOriginal.append(originalCell)
            if len(rowOriginal) > 0: originalEvidence.addRow(rowOriginal)
        originalEvidence.build()
        # originalEvidences.append(originalEvidence)
        return originalEvidence

    def _generateQuery(self, table: Table, evidence: Evidence) -> (str, dict):
        warmSearch = WarmSearch()
        warmSearch.setSeed(self.seed)
        graph = warmSearch.getGraph(evidence, table)
        query, attrMapping = warmSearch.createQuery(graph, table, table.tableName)
        return query, attrMapping

    def _copyTypes(self, tableForType, table):
        for attributeWithType in tableForType.schema:
            header = table.getAttribute(attributeWithType.name)
            header.type = attributeWithType.type

    def _generateNegativeTable(self, table: Table, evidence: Evidence) -> Table:
        refuteGenerator = RefuteInstancesGenerator()
        table = refuteGenerator.generateInstanceForRefuteBigTables(
            table,
            self.addRows,
            self.rowsToAdd,
            self.removeRows,
            self.rowsToRemove,
            self.generationStrategy,
            evidence
        )
        return table

    def _findSemanticQueries(self, database: Database, evidence: Evidence) -> list[SemanticQueryDTO]:
        finder = OperatorFinder(evidence, database, self.operations, self.comparisons)
        finder.exploreAll()
        log.debug("Allowed operations: %s", str(finder.allowedOperations))
        semanticQueries: list[str] = []
        for operation in finder.allowedOperations:
            semanticQuery = operation.printOperator(evidence, database)
            semanticQueries.append(SemanticQueryDTO(name=operation.__str__(), query=semanticQuery))
            log.debug("OPERATION QUERY: %s", operation.__str__())
        log.debug("Semantic queries: %s", semanticQueries)
        return semanticQueries

    def _generateSentences(self, database: Database, evidence: Evidence, task: str, sentenceNumber: int, prompt=None) -> \
    list[str]:
        tenet = Tenet(database, self.seed, self.operations, self.comparisons, bestEvidences=self.bestEvidences,
                      sentencesPerExample=None, languageModel=self.languageModel, rateLimit=self.rateLimit,
                      sleepTime=self.sleepTime, address=self.address)
        if self.disableLanguageModel: tenet.disableLanguageModel()
        prompt = tenet.model.generatePrompt(evidence, task)
        log.debug("Generated Prompt: len %d", len(prompt))
        # print("******** Tenet model: ", tenet.model)
        sentences = tenet.model.generateText(prompt, sentenceNumber)
        return sentences

    def _generateSentencesToExport(self, evidence: Evidence, negative: bool, tableName, table: Table, nSentences,
                                   negativeTable=None) -> list[ExportSentencesDTO]:
        database = Database(tableName)
        if negative:
            database.addTable(negativeTable)
        else:
            database.addTable(table)
        database.inferTypes()
        semantics = self._findSemanticQueries(database, evidence)
        generated: list[ExportSentencesDTO] = []
        for semantic in semantics:
            tenet = Tenet(database, self.seed, self.operations, self.comparisons, bestEvidences=self.bestEvidences,
                          sentencesPerExample=None, languageModel=self.languageModel, rateLimit=self.rateLimit,
                          sleepTime=self.sleepTime)
            if self.disableLanguageModel: tenet.disableLanguageModel()
            prompt = tenet.model.generatePrompt(evidence, semantic.query)
            sentences = tenet.model.generateText(prompt, nSentences)
            log.debug("Generated sentences for semantic %s", semantic.name)
            evidenceForExample = evidence
            if negative:
                evidenceForExample = self._getOriginalEvidenceFromNegative(evidence, table)
            generated.append(
                mapper.exportSentencesToDTO(evidenceForExample, sentences, table, prompt, semantic, negative))
        return generated

    def _batchExampleGeneration(self, tableName, table, userEvidence, nPositives, nNegatives, nSentences) -> list[
        ExportSentencesDTO]:
        response: list[ExportSentencesDTO] = []
        negativeTable = self._generateNegativeTable(table, userEvidence)
        positiveEvidence, positiveQuery, positiveAttrMapping = self._generateEvidence(table, nPositives, userEvidence)
        # negativeEvidence = self._generateEvidence(negativeTable, nNegatives, userEvidence)
        # negativeEvidence = self._generateEvidence(negativeTable, nNegatives, userEvidence)
        negativeEvidence = self._generateNegativeEvidence(negativeTable, nNegatives, userEvidence, positiveQuery,
                                                          positiveAttrMapping)
        log.debug(f"Generated {len(positiveEvidence)} positive evidence")
        log.debug(f"Generated {len(negativeEvidence)} negative evidence")
        for evidence in positiveEvidence:
            response.extend(self._generateSentencesToExport(evidence, False, tableName, table, nSentences))
        for evidence in negativeEvidence:
            response.extend(
                self._generateSentencesToExport(evidence, True, tableName, table, nSentences, negativeTable))
        log.debug("Export Complete!")
        return response
