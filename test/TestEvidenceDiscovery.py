import unittest

from src.model.ColdSearch import ColdSearch
from src.model.RelationalTable import Table, Header, Cell, Database, Evidence
from src.model.WarmSearch import WarmSearch


class TestEvidenceDiscovery(unittest.TestCase):

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

    def test_evidenceSameRowWarm(self):
        warmSearch = WarmSearch()
        table = self.database.getTableByName(self.evidenceSingleRow.tableName)
        #print(table)
        #print(self.evidenceSingleRow)
        graph = warmSearch.getGraph(self.evidenceSingleRow, table)
        #print(graph)
        query, attrMapping = warmSearch.createQuery(graph, table)
        #print(query)
        #print(attrMapping)
        evidences = warmSearch.executeQuery(query, table, attrMapping, 2)
        for e in evidences:
            print(e)
        print("#"*20)
        evidences = warmSearch.findEvidences(table, 2, self.evidenceSingleRow)
        for e in evidences:
            print(e)

    def test_evidenceTwoRowsWarm(self):
        warmSearch = WarmSearch()
        table = self.database.getTableByName(self.evidenceMultipleRows.tableName)
        graph = warmSearch.getGraph(self.evidenceMultipleRows, table)
        query, attrMapping = warmSearch.createQuery(graph, table)
        print(query)
        print(attrMapping)
        evidences = warmSearch.executeQuery(query, table, attrMapping, 5)
        for e in evidences:
            print(e)
            print("*************")
        print("#" * 20)
        evidences = warmSearch.findEvidences(table, 5, self.evidenceMultipleRows)
        for e in evidences:
            print(e)
            print("*************")

    def test_evidenceTwoRowsNumericalWarm(self):
        warmSearch = WarmSearch()
        table = self.database.getTableByName(self.evidenceMultipleRowsNumerical.tableName)
        graph = warmSearch.getGraph(self.evidenceMultipleRowsNumerical, table)
        query, attrMapping = warmSearch.createQuery(graph, table)
        print(query)
        print(attrMapping)
        evidences = warmSearch.executeQuery(query, table, attrMapping, 5)
        for e in evidences:
            print(e)
            print("*************")

    def test_evidenceFullColumnWarm(self):
        warmSearch = WarmSearch()
        table = self.database.getTableByName(self.evidenceFullColumn.tableName)
        graph = warmSearch.getGraph(self.evidenceFullColumn, table)
        query, attrMapping = warmSearch.createQuery(graph, table)
        print(query)
        print(attrMapping)
        evidences = warmSearch.executeQuery(query, table, attrMapping, 5)
        for e in evidences:
            print(e)
            print("*************")

    def test_evidenceCold1(self):
        seed = 17
        coldSearch = ColdSearch()
        coldSearch.setSeed(seed) ## for reproducibylity
        table = self.database.getTableByName("Persons")
        evidences = coldSearch.findEvidences(table, 5, None)
        for e in evidences:
            print(e)
            print("*************")

    def test_evidenceCold2(self):
        seed = 14
        coldSearch = ColdSearch()
        coldSearch.setSeed(seed) ## for reproducibylity
        table = self.database.getTableByName("Persons")
        evidences = coldSearch.findEvidences(table, 5, None)
        for e in evidences:
            print(e)
            print("*************")

    def test_evidenceCold3(self):
        seed = 7
        coldSearch = ColdSearch()
        coldSearch.setSeed(seed) ## for reproducibylity
        coldSearch.setMaxCellsToPick(4)
        table = self.database.getTableByName("University Career")
        evidences = coldSearch.findEvidences(table, 4, None)
        for e in evidences:
            print(e)
            print("*************")