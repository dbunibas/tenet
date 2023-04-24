import unittest

from src.textGeneration.ParserEvidenceGenerator import parseTables


class TestFinder(unittest.TestCase):

    def test_entityTable(self):
        originalTable = []
        originalTable.append(["[H] Name", "Mario"])
        originalTable.append(["[H] Surname", "Rossi"])
        originalTable.append(["[H] Age", "34"])
        name = "EntityTable"
        database = parseTables(originalTable, name)
        print(database)
        print(database.containsNonEmptyTables())
        transposed = list(map(list, zip(*originalTable)))
        database = parseTables(transposed, name)
        database.inferTypes()
        for table in database.tables:
            print(table)
            print(table.schema)

    def test_mixedTable(self):
        originalTable = []
        originalTable.append(["[H] Name", "[H] Surname"])
        originalTable.append(["[H] Age", "xxx"])
        originalTable.append(["[H] Location", "yyy"])
        name = "EntityTable"
        database = parseTables(originalTable, name)
        print(database)

    def test_mixedTabl2(self):
        originalTable = []
        originalTable.append(["[H] Name", "[H] Surname"])
        originalTable.append(["xxx", "zzz"])
        originalTable.append(["kkk", "yyy"])
        name = "EntityTable"
        database = parseTables(originalTable, name)
        print(database)

    def test_mixedTabl4(self):
        originalTable = []
        originalTable.append(["[H] Name", "[H] Surname"])
        originalTable.append(["xxx", "zzz"])
        originalTable.append(["kkk", "yyy"])
        originalTable.append(["[H] Team", "[H] City"])
        originalTable.append(["team1", "city1"])
        originalTable.append(["team2", "city2"])
        name = "EntityTable"
        database = parseTables(originalTable, name)
        print(database)