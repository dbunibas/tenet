import unittest

from src import Constants
from src.model.OperatorAggregativeFunction import OperatorAggregativeFunction
from src.model.OperatorComparison import OperatorComparison
from src.model.OperatorFilter import OperatorFilter
from src.model.OperatorFinder import OperatorFinder
from src.model.OperatorLookup import OperatorLookup
from src.model.OperatorMinMax import OperatorMinMax
from src.model.RelationalTable import Header, Table, Cell, Database, Evidence
from src.textGeneration.ChatGPTLanguageModel import ChatGPTLanguageModel


class TestFinder(unittest.TestCase):

    def setUp(self):
        headerName = Header("Name")
        headerAge = Header("Age")
        headerLoc = Header("Loc")
        table1 = Table("Persons", [headerName, headerAge, headerLoc])
        table1.addRow([Cell("Mike", headerName), Cell(47, headerAge), Cell("SF", headerLoc)])
        table1.addRow([Cell("Anne", headerName), Cell(22, headerAge), Cell("NY", headerLoc)])
        table1.addRow([Cell("John", headerName), Cell(12, headerAge), Cell("NY", headerLoc)])
        table1.addRow([Cell("Paul", headerName), Cell(8, headerAge), Cell("NY", headerLoc)])
        # Name | Age | Loc
        # Mike | 47 | SF
        # Anne | 22 | NY
        # John | 12 | NY
        # Paul | 8 | NY
        #########################################
        headerScore = Header("Score")
        headerExam = Header("Exam")
        table2 = Table("University Career", [headerName, headerScore, headerExam])
        table2.addRow([Cell("Mike", headerName), Cell(10, headerScore), Cell("PP", headerExam)])
        table2.addRow([Cell("Anne", headerName), Cell(9, headerScore), Cell("PP", headerExam)])
        table2.addRow([Cell("Albert", headerName), Cell(8, headerScore), Cell("PP", headerExam)])
        table2.addRow([Cell("Mike", headerName), Cell(8, headerScore), Cell("A1", headerExam)])
        table2.addRow([Cell("Paul", headerName), Cell(4, headerScore), Cell("A1", headerExam)])
        ##########################################
        headerH1 = Header("H1")
        headerH2 = Header("H2")
        headerH3 = Header("H3")
        headerNation = Header("Nation")
        table3 = Table("Health Values", [headerName, headerH1, headerH2, headerH3, headerNation])
        table3.addRow([Cell("Mike", headerName), Cell(10, headerH1), Cell(100, headerH2), Cell(1, headerH3), Cell("ITA", headerNation)])
        table3.addRow([Cell("Anne", headerName), Cell(9, headerH1), Cell(100, headerH2), Cell(2, headerH3), Cell("ITA", headerNation)])
        table3.addRow([Cell("Albert", headerName), Cell(8, headerH1), Cell(100, headerH2), Cell(3, headerH3), Cell("ITA", headerNation)])
        table3.addRow([Cell("Mike", headerName), Cell(7, headerH1), Cell(100, headerH2), Cell(2, headerH3), Cell("FRA", headerNation)])
        table3.addRow([Cell("Paul", headerName), Cell(6, headerH1), Cell(100, headerH2), Cell(3, headerH3), Cell("FRA", headerNation)])
        ##########################################
        headerCandidate = Header("Candidate")
        headerParty = Header("Party")
        headerVotes = Header("Votes")
        table4 = Table("2018 general election: Naples - Fuorigrotta", [headerCandidate, headerParty, headerVotes])
        table4.addRow([Cell("Roberto Fico", headerCandidate), Cell("Five Star", headerParty), Cell(61819, headerVotes)])
        table4.addRow([Cell("Marta Schifone", headerCandidate), Cell("Center right", headerParty), Cell(21651, headerVotes)])
        table4.addRow([Cell("Daniela Iaconis", headerCandidate), Cell("Center left", headerParty), Cell(15779, headerVotes)])
        #Candidate | Party | Votes
        #Roberto Fico | Five Star | 61819
        #Marta Schifone | Center right | 21651
        #Daniela Iaconis | Center left | 15779
        self.database = Database("Test")
        self.database.addTable(table1)
        self.database.addTable(table2)
        self.database.addTable(table3)
        self.database.addTable(table4)
        self.database.inferTypes()
        self.operations = [Constants.OPERATION_LOOKUP, Constants.OPERATION_COMPARISON, Constants.OPERATION_FILTER,
                           Constants.OPERATION_MIN, Constants.OPERATION_MAX, Constants.OPERATION_AVG, Constants.OPERATION_COUNT,
                           Constants.OPERATION_SUM, Constants.OPERATION_RANKED, Constants.OPERATION_PERCENTAGE]
        self.comparisons = [Constants.OPERATOR_SAME, Constants.OPERATOR_LT, Constants.OPERATOR_GT]

    def test_finder_evidence_table1(self):
        # Persons #
        # Name | Age | Loc
        # Mike | 47 | SF
        # Anne | 22 | NY
        # John | 12 | NY
        # Paul | 8 | NY
        evidence1 = Evidence("Persons")
        evidence1.addRow([Cell("Mike", Header("Name")), Cell(47, Header("Age"))])
        evidence1.addRow([Cell("John", Header("Name")), Cell("NY", Header("Loc"))])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        finder = OperatorFinder(evidence1, self.database, self.operations, self.comparisons)
        finder.exploreAll()
        for operator in finder.allowedOperations:
            print(operator.printOperator(evidence1, self.database))
        finder = OperatorFinder(evidence1, self.database, self.operations, self.comparisons)
        finder.exploreAll(composedOperations=True)
        for operator in finder.allowedOperations:
            print(operator.printOperator(evidence1, self.database))

    def test_finder_evidence_table2(self):
        # Persons #
        # Name | Age | Loc
        # Mike | 47 | SF
        # Anne | 22 | NY
        # John | 12 | NY
        # Paul | 8 | NY
        evidence1 = Evidence("Persons")
        evidence1.addRow([Cell("Mike", Header("Name")), Cell(47, Header("Age"))])
        evidence1.addRow([Cell("Anne", Header("Name")), Cell(22, Header("Age"))])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        finder = OperatorFinder(evidence1, self.database, self.operations, self.comparisons)
        finder.exploreAll()
        for operator in finder.allowedOperations:
            print(operator.printOperator(evidence1, self.database))
        print("#"*30)
        finder = OperatorFinder(evidence1, self.database, self.operations, self.comparisons)
        finder.exploreAll(composedOperations=True)
        for operator in finder.allowedOperations:
            print(operator.printOperator(evidence1, self.database))

    def test_finder_evidence_table3(self):
        # Persons #
        # Name | Age | Loc
        # Mike | 47 | SF
        # Anne | 22 | NY
        # John | 12 | NY
        # Paul | 8 | NY
        evidence1 = Evidence("Persons")
        evidence1.addRow([Cell("Anne", Header("Name")), Cell(22, Header("Age")), Cell("NY", Header("Loc"))])
        evidence1.addRow([Cell("John", Header("Name")), Cell(12, Header("Age")), Cell("NY", Header("Loc"))])
        evidence1.addRow([Cell("Paul", Header("Name")), Cell(8, Header("Age")), Cell("NY", Header("Loc"))])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        finder = OperatorFinder(evidence1, self.database, self.operations, self.comparisons)
        finder.exploreAll()
        for operator in finder.allowedOperations:
            print(operator.printOperator(evidence1, self.database))

    def test_finder_evidence_table4(self):
        # Candidate | Party | Votes
        # Roberto Fico | Five Star | 61819
        # Marta Schifone | Center right | 21651
        # Daniela Iaconis | Center left | 15779
        evidence1 = Evidence("2018 general election: Naples - Fuorigrotta")
        evidence1.addRow([Cell("Roberto Fico", Header("Candidate")),Cell("Five Star", Header("Party")),  Cell(61819, Header("Votes"))])
        evidence1.addRow([Cell("Marta Schifone", Header("Candidate")),Cell("Centre right", Header("Party")), Cell(21651, Header("Votes"))])
        evidence1.addRow([Cell("Daniela Iaconis", Header("Candidate")), Cell("Center left", Header("Party")), Cell(15779, Header("Votes"))])
        #evidence1.addRow([Cell("Roberto Fico", Header("Candidate")), Cell("Five Star", Header("Party")), Cell(61819, Header("Votes"))])
        #evidence1.addRow([Cell(21651, Header("Votes"))])
        #evidence1.addRow([Cell(15779, Header("Votes"))])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        finder = OperatorFinder(evidence1, self.database, self.operations, self.comparisons)
        finder.exploreAll()
        # textGenerator = ChatGPTLanguageModel()
        # for operator in finder.allowedOperations:
        #     task = operator.printOperator(evidence1, self.database)
        #     print("Task: ", task)
        #     print(evidence1)
        #     prompt = textGenerator.generatePrompt(evidence1, task)
        #     print(textGenerator.linearizeEvidence(evidence1))
        #     sentences = textGenerator.generateText(prompt)
        #     print("Generated sentences")
        #     for sentence in sentences:
        #         print(sentence)
        #     print("************************")

    def test_finder_with_rank(self):
        # Name | Age | Loc
        # Mike | 47 | SF
        # Anne | 22 | NY
        # John | 12 | NY
        # Paul | 8 | NY
        evidence1 = Evidence("Persons")
        evidence1.addRow([Cell(47, Header("Age"), [0, 1])])
        evidence1.addRow([Cell("Anne", Header("Name"), [1, 0]), Cell(22, Header("Age"), [1, 1])])
        evidence1.addRow([Cell(12, Header("Age"), [2, 1])])
        evidence1.addRow([Cell(8, Header("Age"), [3, 1])])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        finder = OperatorFinder(evidence1, self.database, self.operations, self.comparisons)
        finder.exploreAll()
        for operator in finder.allowedOperations:
            print(operator.printOperator(evidence1, self.database))

    def test_finder_with_rank(self):
        # Name | Age | Loc
        # Mike | 47 | SF
        # Anne | 22 | NY
        # John | 12 | NY
        # Paul | 8 | NY
        evidence1 = Evidence("Persons")
        evidence1.addRow([Cell("Anne", Header("Name"), [1, 0]), Cell(22, Header("Age"), [1, 1])])
        evidence1.addRow([Cell("Mike", Header("Name"), [0, 0]), Cell(47, Header("Age"), [0, 1])])
        evidence1.addRow([Cell("John", Header("Name"), [2, 0]), Cell(12, Header("Age"), [2, 1])])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        finder = OperatorFinder(evidence1, self.database, self.operations, self.comparisons)
        finder.exploreAll()
        for operator in finder.allowedOperations:
            print(operator.printOperator(evidence1, self.database))


