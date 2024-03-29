import unittest

from src import Constants
from src.model.RefuteInstancesGenerator import RefuteInstancesGenerator
from src.model.RelationalTable import Table, Header, Cell, Database, Evidence


class TestGenerateRefuteInstance(unittest.TestCase):

    def setUp(self):
        headerName = Header("Name")
        headerAge = Header("Age")
        headerLoc = Header("Loc")
        table1 = Table("Persons", [headerName, headerAge, headerLoc])
        table1.addRow([Cell("Mike", headerName), Cell(47, headerAge), Cell("SF", headerLoc)])
        table1.addRow([Cell("Anne", headerName), Cell(22, headerAge), Cell("NY", headerLoc)])
        table1.addRow([Cell("John", headerName), Cell(12, headerAge), Cell("NY", headerLoc)])
        table1.addRow([Cell("Paul", headerName), Cell(8, headerAge), Cell("NY", headerLoc)])
        table1.initPosForCells()
        headerScore = Header("Score")
        headerExam = Header("Exam")
        table2 = Table("University Career", [headerName, headerScore, headerExam])
        table2.addRow([Cell("Mike", headerName), Cell(10, headerScore), Cell("PP", headerExam)])
        table2.addRow([Cell("Mike", headerName), Cell(9, headerScore), Cell("POOI", headerExam)])
        table2.addRow([Cell("John", headerName), Cell(8, headerScore), Cell("A1", headerExam)])
        table2.addRow([Cell("Paul", headerName), Cell(4, headerScore), Cell("NET1", headerExam)])
        table2.initPosForCells()
        self.database = Database("Test")
        self.database.addTable(table1)
        self.database.addTable(table2)
        self.database.inferTypes()

    def tearDown(self):
        pass

    def test_gererateFromRandom(self):
        generator = RefuteInstancesGenerator()
        table = self.database.getTableByName("Persons")
        print(table)
        shuffled = generator.shuffleInstance(table)
        print(shuffled)

    def test_removeFromInstance(self):
        generator = RefuteInstancesGenerator()
        table = self.database.getTableByName("Persons")
        print(table)
        removed = generator.removeTuple(table, 20)
        print(removed)
        removed = generator.removeTuple(table, 2)
        print(removed)

    def test_addRowToInstanceWithActiveDomain(self):
        generator = RefuteInstancesGenerator()
        table = self.database.getTableByName("Persons")
        print(table)
        added = generator.addTuple(table, 2, Constants.STRATEGY_ACTIVE_DOMAIN, Constants.STRATEGY_CHANGE_MAX)
        print(added)

    def test_generateRefuteInstanceWithAdd(self):
        generator = RefuteInstancesGenerator()
        table = self.database.getTableByName("Persons")
        print(table)
        added = generator.generateInstanceForRefute(table, True, 4, False, 0, Constants.STRATEGY_ACTIVE_DOMAIN)
        print(added)

    def test_generateRefuteInstanceWithRemove(self):
        generator = RefuteInstancesGenerator()
        table = self.database.getTableByName("Persons")
        print(table)
        removed = generator.generateInstanceForRefute(table, False, 0, True, 2, Constants.STRATEGY_ACTIVE_DOMAIN)
        print(removed)

    def test_generateRefuteInstanceWithAdd(self):
        generator = RefuteInstancesGenerator()
        generator.useLM()  ## to load the LM
        table = self.database.getTableByName("Persons")
        print(table)
        added = generator.generateInstanceForRefute(table, True, 4, False, 0, Constants.STRATEGY_LM_GENERATOR)
        print(added)
