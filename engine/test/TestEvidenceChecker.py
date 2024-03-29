import unittest

from src import Constants
from src.model.RelationalTable import Table, Header, Cell, Database, Evidence
from src.textGeneration.EvidenceChecker import checkEvidenceForGrouping
from src.textGeneration.RunnerEvidenceChecker import findAllowedOperations
from src.textGeneration.TextGenerator import TextGenerator


class TestEvidenceChecker(unittest.TestCase):

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

    def tearDown(self):
        pass

    def test_check1(self):
        # print(self.database)
        evidence1 = Evidence("Persons")
        evidence1.addRow([Cell("Mike", Header("Name")), Cell(47, Header("Age"))])
        evidence1.addRow([Cell("Anne", Header("Name")), Cell(22, Header("Age"))])
        evidence1.addRow([Cell("John", Header("Name")), Cell(12, Header("Age"))])
        evidence1.build()
        check, attributeName, value = checkEvidenceForGrouping(evidence1, self.database, Constants.OPERATOR_SAME)
        self.assertFalse(check, "Groping with same false")
        check, attributeName, value = checkEvidenceForGrouping(evidence1, self.database, Constants.OPERATOR_GT)
        self.assertTrue(check, "Grouping with greater than true")
        self.assertTrue(attributeName == "Age", "Attribute should be age")
        self.assertTrue(value == 8, "Value should be 8")
        check, attributeName, value = checkEvidenceForGrouping(evidence1, self.database, Constants.OPERATOR_LT)
        self.assertFalse(check, "Groping with lower false")

    def test_check2(self):
        evidence1 = Evidence("Persons")
        evidence1.addRow([Cell("Anne", Header("Name")), Cell("NY", Header("Loc"))])
        evidence1.addRow([Cell("Paul", Header("Name")), Cell("NY", Header("Loc"))])
        evidence1.addRow([Cell("John", Header("Name")), Cell("NY", Header("Loc"))])
        evidence1.build()
        check, attributeName, value = checkEvidenceForGrouping(evidence1, self.database, Constants.OPERATOR_SAME)
        self.assertTrue(check, "Groping with same true")
        self.assertTrue(attributeName == "Loc", "Attribute should be loc")
        self.assertTrue(value == "NY", "Value should be NY")
        check, attributeName, value = checkEvidenceForGrouping(evidence1, self.database, Constants.OPERATOR_GT)
        self.assertFalse(check, "Groping with GT false")
        check, attributeName, value = checkEvidenceForGrouping(evidence1, self.database, Constants.OPERATOR_LT)
        self.assertFalse(check, "Groping with LT false")

    def test_check3(self):
        evidence1 = Evidence("Persons")
        evidence1.addRow([Cell("NY", Header("Loc"))])
        evidence1.addRow([Cell("NY", Header("Loc"))])
        evidence1.addRow([Cell("NY", Header("Loc"))])
        evidence1.addRow([Cell("NY", Header("Loc"))])
        evidence1.build()
        check, attributeName, value = checkEvidenceForGrouping(evidence1, self.database, Constants.OPERATOR_SAME)
        print(check, attributeName, value)
        self.assertFalse(check, "Groping with same false, since there are no 4 NY values in table")

    def test_check4(self):
        ops = [Constants.OPERATION_MIN, Constants.OPERATION_MAX, Constants.OPERATION_COUNT, Constants.OPERATION_LOOKUP,
               Constants.OPERATION_COMPARISON, Constants.OPERATION_GROUPING]
        comparisons = [Constants.OPERATOR_LT, Constants.OPERATOR_GT, Constants.OPERATOR_SAME]
        evidence1 = Evidence("Persons")
        evidence1.addRow([Cell("Mike", Header("Name")), Cell(47, Header("Age"))])
        evidence1.addRow([Cell("Anne", Header("Name")), Cell(22, Header("Age"))])
        evidence1.addRow([Cell("John", Header("Name")), Cell(12, Header("Age"))])
        #####
        # evidence1.addRow([Cell("Anne", Header("Name")), Cell("NY", Header("Loc"))])
        # evidence1.addRow([Cell("Paul", Header("Name")), Cell("NY", Header("Loc"))])
        # evidence1.addRow([Cell("John", Header("Name")), Cell("NY", Header("Loc"))])
        evidence1.build()
        allowedOP = findAllowedOperations(evidence1, self.database, ops, comparisons)
        print(allowedOP)
