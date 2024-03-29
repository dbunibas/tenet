import unittest

from src import Constants
from src.Tenet import Tenet
from src.model.RelationalTable import Table, Header, Cell, Database, Evidence


class TestTenet(unittest.TestCase):

    def setUp(self):
        headerName = Header("Name")
        headerAge = Header("Age")
        headerLoc = Header("Loc")
        table1 = Table("Persons", [headerName, headerAge, headerLoc])
        table1.addRow([Cell("Mike", headerName), Cell(47, headerAge), Cell("SF", headerLoc)])
        table1.addRow([Cell("Anne", headerName), Cell(22, headerAge), Cell("NY", headerLoc)])
        table1.addRow([Cell("John", headerName), Cell(12, headerAge), Cell("NY", headerLoc)])
        table1.addRow([Cell("Paul", headerName), Cell(8, headerAge), Cell("NY", headerLoc)])
        headerScore = Header("Score")
        headerExam = Header("Exam")
        table2 = Table("University Career", [headerName, headerScore, headerExam])
        table2.addRow([Cell("Mike", headerName), Cell(10, headerScore), Cell("PP", headerExam)])
        table2.addRow([Cell("Mike", headerName), Cell(9, headerScore), Cell("POOI", headerExam)])
        table2.addRow([Cell("John", headerName), Cell(8, headerScore), Cell("A1", headerExam)])
        table2.addRow([Cell("Paul", headerName), Cell(4, headerScore), Cell("NET1", headerExam)])
        self.database = Database("Test")
        self.database.addTable(table1)
        self.database.addTable(table2)
        self.database.inferTypes()

        self.evidenceSingleRow = Evidence("Persons")
        cell0_0 = Cell("Mike", Header("Name"))
        cell0_0.setPos([0, 0])
        cell0_1 = Cell(47, Header("Age"))
        cell0_1.setPos([0, 1])
        self.evidenceSingleRow.addRow([cell0_0, cell0_1])
        self.evidenceSingleRow.build()

        self.evidenceMultipleRows = Evidence("Persons")
        cell0_2 = Cell("SF", Header("Loc"))
        cell0_2.setPos([0, 2])
        self.evidenceMultipleRows.addRow([cell0_0, cell0_2])
        cell1_0 = Cell("Anne", Header("Name"))
        cell1_0.setPos([1, 0])
        cell1_1 = Cell(22, Header("Age"))
        cell1_1.setPos([1, 1])
        cell1_2 = Cell("NY", Header("Loc"))
        cell1_2.setPos([1, 2])
        self.evidenceMultipleRows.addRow([cell1_0, cell1_2])
        self.evidenceMultipleRows.build()

        self.evidenceMultipleRowsNumerical = Evidence("Persons")
        cell0_2 = Cell("SF", Header("Loc"))
        cell0_2.setPos([0, 2])
        self.evidenceMultipleRowsNumerical.addRow([cell0_0, cell0_1])
        cell1_0 = Cell("Anne", Header("Name"))
        cell1_0.setPos([1, 0])
        cell1_1 = Cell(22, Header("Age"))
        cell1_1.setPos([1, 1])
        cell1_2 = Cell("NY", Header("Loc"))
        cell1_2.setPos([1, 2])
        self.evidenceMultipleRowsNumerical.addRow([cell1_0, cell1_1])
        self.evidenceMultipleRowsNumerical.build()

        self.evidenceFullColumn = Evidence("Persons")
        self.evidenceFullColumn.addRow([cell0_0, cell0_1])
        self.evidenceFullColumn.addRow([cell1_1])
        cell2_1 = Cell(12, Header("Age"))
        cell2_1.setPos([2, 1])
        self.evidenceFullColumn.addRow([cell2_1])
        cell3_1 = Cell(18, Header("Age"))
        cell3_1.setPos([3, 1])
        self.evidenceFullColumn.addRow([cell3_1])
        self.evidenceFullColumn.build()

    def tearDown(self):
        pass

    def test_generate_singleEvidenceAddRows(self):
        tableName = self.evidenceSingleRow.tableName
        evidenceSel = self.evidenceSingleRow
        numEvidence = 10  ## generated evidences, filtered with bestEvidences
        addRows = True
        rowsToAdd = 3
        removeRows = False
        rowsToRemove = 0
        useLM = False
        strategy = Constants.STRATEGY_ACTIVE_DOMAIN
        if strategy == Constants.STRATEGY_LM_GENERATOR:
            useLM = True
        seed = 17
        operations = [Constants.OPERATION_LOOKUP, Constants.OPERATION_COMPARISON, Constants.OPERATION_FILTER,
                      Constants.OPERATION_MIN, Constants.OPERATION_MAX, Constants.OPERATION_COUNT,
                      Constants.OPERATION_SUM, Constants.OPERATION_AVG]
        comparisons = [Constants.OPERATOR_SAME, Constants.OPERATOR_LT, Constants.OPERATOR_GT]
        languageModel = Constants.LANGUAGE_MODEL_CHAT_GTP
        bestEvidences = 5
        sentencesPerExample = 3
        rateLimit = True
        sleepTime = 21  ## rateLimit 3 requests per minute
        tenet = Tenet(self.database, seed, operations, comparisons, bestEvidences, sentencesPerExample, languageModel,
                      rateLimit, sleepTime)
        tenet.disableLanguageModel()
        positiveExamples = tenet.generatePositiveExamples(tableName, evidenceSel, numEvidence)
        negativeExamples = tenet.generateNegativeExamples(tableName, evidenceSel, numEvidence, addRows, rowsToAdd,
                                                          removeRows, rowsToRemove, strategy, useLM=useLM)
        table = self.database.getTableByName(tableName)
        print(table)
        print("***** POSITIVES *****")
        for p in positiveExamples:
            print(p["evidence"])
            print(p["sentences"])
        print("***** NEGATIVES *****")
        for n in negativeExamples:
            print(n["evidence"])
            print(n["sentences"])

    def test_generate_evidenceMultipleRowsNumerical(self):
        tableName = self.evidenceMultipleRowsNumerical.tableName
        evidenceSel = self.evidenceMultipleRowsNumerical
        numEvidence = 10  ## generated evidences, filtered with bestEvidences
        addRows = True
        rowsToAdd = 3
        removeRows = False
        rowsToRemove = 0
        useLM = False
        strategy = Constants.STRATEGY_ACTIVE_DOMAIN
        if strategy == Constants.STRATEGY_LM_GENERATOR:
            useLM = True
        seed = 17
        operations = [Constants.OPERATION_LOOKUP, Constants.OPERATION_COMPARISON, Constants.OPERATION_FILTER,
                      Constants.OPERATION_MIN, Constants.OPERATION_MAX, Constants.OPERATION_COUNT,
                      Constants.OPERATION_SUM, Constants.OPERATION_AVG]
        comparisons = [Constants.OPERATOR_SAME, Constants.OPERATOR_LT, Constants.OPERATOR_GT]
        languageModel = Constants.LANGUAGE_MODEL_CHAT_GTP
        bestEvidences = 5
        sentencesPerExample = 3
        rateLimit = True
        sleepTime = 21  ## rateLimit 3 requests per minute
        tenet = Tenet(self.database, seed, operations, comparisons, bestEvidences, sentencesPerExample, languageModel,
                      rateLimit, sleepTime)
        ## if evidenceSel is None then Cold
        positiveExamples = tenet.generatePositiveExamples(tableName, evidenceSel, numEvidence)
        negativeExamples = tenet.generateNegativeExamples(tableName, evidenceSel, numEvidence, addRows, rowsToAdd,
                                                          removeRows, rowsToRemove, strategy, useLM=useLM)
        table = self.database.getTableByName(tableName)
        print(table)
        print("***** POSITIVES *****")
        for p in positiveExamples:
            print(p["evidence"])
            print(p["sentences"])
        print("***** NEGATIVES *****")
        for n in negativeExamples:
            print(n["evidence"])
            print(n["sentences"])
