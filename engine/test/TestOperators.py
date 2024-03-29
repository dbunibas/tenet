import unittest

from src import Constants
from src.model.OperatorRankedSimple import OperatorRankedSimple
from src.model.OperatorAggregativeFunction import OperatorAggregativeFunction
from src.model.OperatorComparison import OperatorComparison
from src.model.OperatorFilter import OperatorFilter
from src.model.OperatorLookup import OperatorLookup
from src.model.OperatorMinMax import OperatorMinMax
from src.model.OperatorPercentage import OperatorPercentage
from src.model.OperatorRanked import OperatorRanked
from src.model.RelationalTable import Header, Table, Cell, Database, Evidence


class TestOperator(unittest.TestCase):

    def setUp(self):
        headerName = Header("Name")
        headerAge = Header("Age")
        headerLoc = Header("Loc")
        table1 = Table("Persons", [headerName, headerAge, headerLoc])
        table1.addRow([Cell("Mike", headerName), Cell(47, headerAge), Cell("SF", headerLoc)])
        table1.addRow([Cell("Anne", headerName), Cell(22, headerAge), Cell("NY", headerLoc)])
        table1.addRow([Cell("John", headerName), Cell(12, headerAge), Cell("NY", headerLoc)])
        table1.addRow([Cell("Paul", headerName), Cell(8, headerAge), Cell("NY", headerLoc)])
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
        table3.addRow([Cell("Mike", headerName), Cell(10, headerH1), Cell(100, headerH2), Cell(1, headerH3),
                       Cell("ITA", headerNation)])
        table3.addRow([Cell("Anne", headerName), Cell(9, headerH1), Cell(100, headerH2), Cell(2, headerH3),
                       Cell("ITA", headerNation)])
        table3.addRow([Cell("Albert", headerName), Cell(8, headerH1), Cell(100, headerH2), Cell(3, headerH3),
                       Cell("ITA", headerNation)])
        table3.addRow([Cell("Mike", headerName), Cell(7, headerH1), Cell(100, headerH2), Cell(2, headerH3),
                       Cell("FRA", headerNation)])
        table3.addRow([Cell("Paul", headerName), Cell(6, headerH1), Cell(100, headerH2), Cell(3, headerH3),
                       Cell("FRA", headerNation)])
        self.database = Database("Test")
        self.database.addTable(table1)
        self.database.addTable(table2)
        self.database.addTable(table3)
        self.database.inferTypes()

    def test_lookup(self):
        evidence1 = Evidence("Persons")
        evidence1.addRow([Cell("Mike", Header("Name")), Cell(47, Header("Age"))])
        evidence1.addRow([Cell("Anne", Header("Name")), Cell(22, Header("Age"))])
        evidence1.addRow([Cell("John", Header("Name")), Cell(12, Header("Age"))])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operator = OperatorLookup()
        check = operator.checkSemantic(evidence1, self.database)
        # print("Check Lookup:", check)
        self.assertTrue(check, "Evidence 1")
        # if check: print("Operation:", operator.printOperator(evidence1, self.database))
        evidence2 = Evidence("Persons")
        for i in range(0, 10):
            evidence2.addRow([Cell("Mike", Header("Name")), Cell(47, Header("Age"))])
            evidence2.addRow([Cell("Anne", Header("Name")), Cell(22, Header("Age"))])
            evidence2.addRow([Cell("John", Header("Name")), Cell(12, Header("Age"))])
        evidence2.build()
        evidence2.inferTypesFromDB(self.database)
        check = operator.checkSemantic(evidence2, self.database)
        # print("Check Lookup:", check)
        self.assertFalse(check, "Evidence 2")

    def test_comparisons(self):
        evidence1 = Evidence("Persons")
        evidence1.addRow([Cell("Mike", Header("Name")), Cell(47, Header("Age"))])
        evidence1.addRow([Cell("Anne", Header("Name")), Cell(22, Header("Age"))])
        evidence1.addRow([Cell("John", Header("Name")), Cell(12, Header("Age"))])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorName = OperatorComparison("Name", Constants.OPERATOR_SAME);
        operatorNameGT = OperatorComparison("Name", Constants.OPERATOR_GT);
        operatorAgeGT = OperatorComparison("Age", Constants.OPERATOR_GT)
        operatorAgeLT = OperatorComparison("Age", Constants.OPERATOR_LT)
        operatorAgeSame = OperatorComparison("Age", Constants.OPERATOR_SAME)
        self.assertFalse(operatorName.checkSemantic(evidence1, self.database), "Name should not be compared with =")
        self.assertFalse(operatorNameGT.checkSemantic(evidence1, self.database), "Name should not be compared with >")
        self.assertTrue(operatorAgeGT.checkSemantic(evidence1, self.database), "Age can be compared with >")
        self.assertTrue(operatorAgeLT.checkSemantic(evidence1, self.database), "Age can be compared with <")
        self.assertFalse(operatorAgeSame.checkSemantic(evidence1, self.database), "Age cannot be compared with =")
        # print(operatorAgeGT.printOperator(evidence1, self.database))
        # print(operatorAgeLT.printOperator(evidence1, self.database))

        evidence2 = Evidence("Persons")
        evidence2.addRow([Cell("Paul", Header("Name")), Cell(8, Header("Age")), Cell("NY", Header("Loc"))])
        evidence2.addRow([Cell("Anne", Header("Name")), Cell(22, Header("Age")), Cell("NY", Header("Loc"))])
        evidence2.addRow([Cell("John", Header("Name")), Cell(12, Header("Age")), Cell("NY", Header("Loc"))])
        evidence2.build()
        evidence2.inferTypesFromDB(self.database)
        self.assertTrue(operatorAgeGT.checkSemantic(evidence2, self.database), "Age can be compared with >")
        self.assertTrue(operatorAgeLT.checkSemantic(evidence2, self.database), "Age can be compared with <")
        operatorLocSame = OperatorComparison("Loc", Constants.OPERATOR_SAME)
        self.assertTrue(operatorLocSame.checkSemantic(evidence2, self.database), "Loc can be compared with = ")
        # print(operatorLocSame.printOperator(evidence2, self.database))

    def test_filter(self):
        evidence1 = Evidence("Persons")
        evidence1.addRow([Cell("Mike", Header("Name")), Cell(47, Header("Age"))])
        evidence1.addRow([Cell("Anne", Header("Name")), Cell(22, Header("Age"))])
        evidence1.addRow([Cell("John", Header("Name")), Cell(12, Header("Age"))])
        evidence1.addRow([Cell("Paul", Header("Name")), Cell(8, Header("Age"))])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorFilterName = OperatorFilter("Name", Constants.OPERATOR_SAME)
        operatorFilterAge = OperatorFilter("Age", Constants.OPERATOR_GT)
        self.assertFalse(operatorFilterName.checkSemantic(evidence1, self.database),
                         "It is not a filter because because there are multiple vulues selected")
        self.assertFalse(operatorFilterAge.checkSemantic(evidence1, self.database),
                         "It is not a filter because there are multiple values selected")

        evidence2 = Evidence("Persons")
        evidence2.addRow([Cell("Anne", Header("Name")), Cell(22, Header("Age")), Cell("NY", Header("Loc"))])
        evidence2.addRow([Cell("Paul", Header("Name")), Cell(8, Header("Age")), Cell("NY", Header("Loc"))])
        evidence2.addRow([Cell("John", Header("Name")), Cell(12, Header("Age")), Cell("NY", Header("Loc"))])
        evidence2.build()
        evidence2.inferTypesFromDB(self.database)
        operatorFilterLoc = OperatorFilter("Loc", Constants.OPERATOR_SAME)
        self.assertTrue(operatorFilterLoc.checkSemantic(evidence2, self.database),
                        "It is a filter since we selected all the 3 values of NY")

        evidence3 = Evidence("Persons")
        evidence3.addRow([Cell("Anne", Header("Name")), Cell(22, Header("Age")), Cell("NY", Header("Loc"))])
        evidence3.addRow([Cell("John", Header("Name")), Cell(12, Header("Age")), Cell("NY", Header("Loc"))])
        evidence3.build()
        evidence3.inferTypesFromDB(self.database)
        operatorFilterLoc = OperatorFilter("Loc", Constants.OPERATOR_SAME)
        self.assertFalse(operatorFilterLoc.checkSemantic(evidence3, self.database),
                         "It is not a filter since we selected 2 of 3 values of NY in database")

        evidence4 = Evidence("Persons")
        evidence4.addRow([Cell("John", Header("Name")), Cell(12, Header("Age"))])
        evidence4.addRow([Cell("Mike", Header("Name")), Cell(47, Header("Age"))])
        evidence4.addRow([Cell("Anne", Header("Name")), Cell(22, Header("Age"))])
        # evidence4.addRow([Cell("Paul", Header("Name")), Cell(8, Header("Age"))])
        evidence4.build()
        evidence4.inferTypesFromDB(self.database)
        operatorAgeGreater = OperatorFilter("Age", Constants.OPERATOR_GT)
        self.assertTrue(operatorAgeGreater.checkSemantic(evidence4, self.database),
                        "It is a filter since we selected all the people with age > 8")
        self.assertTrue(operatorAgeGreater.value == 8, "The value for the filter is 8")

        evidence4.addRow([Cell("Paul", Header("Name")), Cell(8, Header("Age"))])
        evidence4.build()
        evidence4.inferTypesFromDB(self.database)
        operatorAgeGreater = OperatorFilter("Age", Constants.OPERATOR_GT)
        self.assertFalse(operatorAgeGreater.checkSemantic(evidence4, self.database),
                         "It is not a filter since we selected all the people")

        evidence5 = Evidence("Persons")
        evidence5.addRow([Cell("John", Header("Name")), Cell(12, Header("Age"))])
        evidence5.addRow([Cell("Paul", Header("Name")), Cell(8, Header("Age"))])
        evidence5.build()
        evidence5.inferTypesFromDB(self.database)
        operatorAgeLower = OperatorFilter("Age", Constants.OPERATOR_LT)
        self.assertTrue(operatorAgeLower.checkSemantic(evidence5, self.database),
                        "It is a filter since we selected all the people with age < 22")
        self.assertTrue(operatorAgeLower.value == 22, "The value for the filter is 22")
        operatorAgeGreater = OperatorFilter("Age", Constants.OPERATOR_GT)
        self.assertFalse(operatorAgeGreater.checkSemantic(evidence5, self.database),
                         "It is not a filter since we selected all the people with age < 22 and not with age greater than something")

    def test_minMax(self):
        evidence1 = Evidence("Persons")
        evidence1.addRow([Cell("Mike", Header("Name")), Cell(47, Header("Age"))])
        evidence1.addRow([Cell("Anne", Header("Name")), Cell(22, Header("Age"))])
        evidence1.addRow([Cell("John", Header("Name")), Cell(12, Header("Age"))])
        evidence1.addRow([Cell("Paul", Header("Name")), Cell(8, Header("Age"))])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)

        operatorNameMin = OperatorMinMax("Name", Constants.OPERATION_MIN)
        operatorAgeMin = OperatorMinMax("Age", Constants.OPERATION_MIN)
        operatorAgeMax = OperatorMinMax("Age", Constants.OPERATION_MAX)
        self.assertFalse(operatorNameMin.checkSemantic(evidence1, self.database),
                         "It is not a min-max op since the attribute is categorical")
        self.assertTrue(operatorAgeMin.checkSemantic(evidence1, self.database),
                        "The evidence contains the min in the table")
        self.assertTrue(operatorAgeMax.checkSemantic(evidence1, self.database),
                        "The evidence contains the max in the table")

        evidence2 = Evidence("Persons")
        evidence2.addRow([Cell("Mike", Header("Name")), Cell(46, Header("Age"))])
        evidence2.addRow([Cell("Anne", Header("Name")), Cell(22, Header("Age"))])
        evidence2.addRow([Cell("John", Header("Name")), Cell(12, Header("Age"))])
        evidence2.addRow([Cell("Paul", Header("Name")), Cell(16, Header("Age"))])
        evidence2.build()
        evidence2.inferTypesFromDB(self.database)
        self.assertFalse(operatorAgeMin.checkSemantic(evidence2, self.database),
                         "The evidence doesn't contain the min in the table")
        self.assertFalse(operatorAgeMax.checkSemantic(evidence2, self.database),
                         "The evidence doesn't contain the max in the table")

        evidence3 = Evidence("Persons")
        evidence3.addRow([Cell("Mike", Header("Name")), Cell(47, Header("Age"))])
        evidence3.addRow([Cell("Paul", Header("Name")), Cell(8, Header("Age"))])
        evidence3.build()
        evidence3.inferTypesFromDB(self.database)
        self.assertFalse(operatorAgeMin.checkSemantic(evidence3, self.database),
                         "The evidence doesn't cover the full table")
        self.assertFalse(operatorAgeMax.checkSemantic(evidence3, self.database),
                         "The evidence doesn't cover the full table")

    def test_aggregativeFunction(self):
        evidence1 = Evidence("Persons")
        evidence1.addRow([Cell("Mike", Header("Name")), Cell(47, Header("Age"))])
        evidence1.addRow([Cell("Anne", Header("Name")), Cell(22, Header("Age"))])
        evidence1.addRow([Cell("John", Header("Name")), Cell(12, Header("Age"))])
        evidence1.addRow([Cell("Paul", Header("Name")), Cell(8, Header("Age"))])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorAVGName = OperatorAggregativeFunction("Name", Constants.OPERATION_AVG)
        self.assertFalse(operatorAVGName.checkSemantic(evidence1, self.database),
                         "The evidence of Name cannot be an avg function, even if we select the whole columns")
        operatorAVGName.setFilter("Age", Constants.OPERATOR_GT)
        self.assertFalse(operatorAVGName.checkSemantic(evidence1, self.database),
                         "The evidence of Name cannot be an avg function, even if we select the filter")

        evidence2 = Evidence("Persons")
        evidence2.addRow([Cell("Mike", Header("Name")), Cell(47, Header("Age"))])
        evidence2.addRow([Cell("Anne", Header("Name")), Cell(22, Header("Age"))])
        evidence2.addRow([Cell("John", Header("Name")), Cell(12, Header("Age"))])
        evidence2.build()
        evidence2.inferTypesFromDB(self.database)
        ## filter age > 8
        operatorSumName = OperatorAggregativeFunction("Name", Constants.OPERATION_SUM)
        self.assertFalse(operatorSumName.checkSemantic(evidence2, self.database),
                         "The evidence of Name cannot be a sum function, even if we select the whole columns")
        operatorSumName.setFilter("Age", Constants.OPERATOR_GT)
        self.assertFalse(operatorSumName.checkSemantic(evidence2, self.database),
                         "The evidence of Name cannot be a sum function, even if we select the filter")

        evidence3 = Evidence("Persons")
        evidence3.addRow([Cell(47, Header("Age"))])
        evidence3.addRow([Cell(22, Header("Age"))])
        evidence3.addRow([Cell(12, Header("Age"))])
        evidence3.build()
        evidence3.inferTypesFromDB(self.database)
        operatorCountAge = OperatorAggregativeFunction("Age", Constants.OPERATION_COUNT)
        operatorAVGAge = OperatorAggregativeFunction("Age", Constants.OPERATION_AVG)
        operatorSumAge = OperatorAggregativeFunction("Age", Constants.OPERATION_SUM)
        self.assertFalse(operatorCountAge.checkSemantic(evidence3, self.database),
                         "The evidence is not a count function, since we didn't select the whole column")
        self.assertFalse(operatorAVGAge.checkSemantic(evidence3, self.database),
                         "The evidence is not an avg function, since we didn't select the whole column")
        self.assertFalse(operatorSumAge.checkSemantic(evidence3, self.database),
                         "The evidence is not a sum function, since we didn't select the whole column")

        evidence4 = Evidence("Persons")
        evidence4.addRow([Cell(47, Header("Age"))])
        evidence4.addRow([Cell(22, Header("Age"))])
        evidence4.addRow([Cell(12, Header("Age"))])
        evidence4.addRow([Cell(8, Header("Age"))])
        evidence4.build()
        evidence4.inferTypesFromDB(self.database)
        self.assertTrue(operatorCountAge.checkSemantic(evidence4, self.database),
                        "The evidence is a count function, since we didn't select the whole column")
        self.assertTrue(operatorAVGAge.checkSemantic(evidence4, self.database),
                        "The evidence is an avg function, since we didn't select the whole column")
        self.assertTrue(operatorSumAge.checkSemantic(evidence4, self.database),
                        "The evidence is a sum function, since we didn't select the whole column")
        self.assertTrue(operatorCountAge.value == 4, "There are four elements in the table")
        self.assertTrue(operatorAVGAge.value == (sum([47, 22, 12, 8]) / len([47, 22, 12, 8])),
                        "The mean is " + str(sum([47, 22, 12, 8]) / len([47, 22, 12, 8])))
        self.assertTrue(operatorSumAge.value == sum([47, 22, 12, 8]), "The sum is " + str(sum([47, 22, 12, 8])))

        evidence5 = Evidence("Health Values")
        evidence5.addRow(
            [Cell("Mike", Header("Name")), Cell(10, Header("H1")), Cell(100, Header("H2")), Cell(1, Header("H3"))])
        evidence5.addRow(
            [Cell("Anne", Header("Name")), Cell(9, Header("H1")), Cell(100, Header("H2")), Cell(2, Header("H3"))])
        evidence5.addRow(
            [Cell("Albert", Header("Name")), Cell(8, Header("H1")), Cell(100, Header("H2")), Cell(3, Header("H3"))])
        evidence5.build()
        evidence5.inferTypesFromDB(self.database)
        operatorCountH2 = OperatorAggregativeFunction("H2", Constants.OPERATION_COUNT)
        self.assertFalse(operatorCountH2.checkSemantic(evidence5, self.database),
                         "it is not a count since we didn't select the whole table")
        operatorCountH2.setFilter("H1", Constants.OPERATOR_LT)
        self.assertFalse(operatorCountH2.checkSemantic(evidence5, self.database),
                         "it is not a count since there are others entities with lower values")
        operatorCountH2.setFilter("H1", Constants.OPERATOR_GT)
        self.assertTrue(operatorCountH2.checkSemantic(evidence5, self.database),
                        "it is a count since there is a filter with values > 7 for H1")
        self.assertTrue(operatorCountH2.operatorFilter.value == 7, "the filter value is 7")
        self.assertTrue(operatorCountH2.value == 3, "the count is 3")

    def test_aggregativeFunction2(self):
        headerCause = Header("Cause of Death")
        header19th = Header("19 th")
        header21st = Header("21 st")
        table1 = Table("Mohmand Expedition of 1908", [headerCause, header19th, header21st])
        table1.addRow([Cell("K bullets", headerCause), Cell(9, header19th), Cell(4, header21st)])
        table1.addRow([Cell("W bullets", headerCause), Cell(6, header19th), Cell(0, header21st)])
        table1.addRow([Cell("Inj wire", headerCause), Cell(8, header19th), Cell(2, header21st)])
        table1.addRow([Cell("Missing", headerCause), Cell(24, header19th), Cell(6, header21st)])
        database = Database("DB")
        database.addTable(table1)
        database.inferTypes()

        evidence1 = Evidence("Mohmand Expedition of 1908")
        # evidence1.addRow([Cell("K bullets", headerCause), Cell(8, header19th)])
        evidence1.addRow([Cell("W bullets", headerCause), Cell(6, header19th)])
        evidence1.addRow([Cell("Inj wire", headerCause), Cell(8, header19th), Cell(2, header21st)])
        evidence1.build()
        evidence1.inferTypesFromDB(database)

        operatorAggregative = OperatorAggregativeFunction("21 st", Constants.OPERATION_AVG)
        operatorAggregative.setFilter("19 th", Constants.OPERATOR_LT)
        check = operatorAggregative.checkSemantic(evidence1, database)
        self.assertFalse(check, "cannot apply a filter since the values in 19th are all  different")
        if check: print(operatorAggregative.printOperator(evidence1, database))

    def test_rankedFunction(self):
        evidence1 = Evidence("University Career")
        evidence1.addRow([Cell(10, Header("Score"), [0, 1])])
        evidence1.addRow([Cell("Anne", Header("Name"), [1, 0]), Cell(9, Header("Score"), [1, 1])])
        evidence1.addRow([Cell(8, Header("Score"), [2, 1])])
        evidence1.addRow([Cell(8, Header("Score"), [3, 1])])
        evidence1.addRow([Cell(4, Header("Score"), [4, 1])])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorRanked = OperatorRanked("Score", "Name")
        check = operatorRanked.checkSemantic(evidence1, self.database)
        self.assertTrue(check, "Ranked Function can be applied")
        self.assertTrue(operatorRanked.value == 9, "Selected value is 9")
        self.assertTrue(operatorRanked.orderType == "desc", "It is close to the right side (ordered asc)")
        self.assertTrue(operatorRanked.pos == 2, "It is the 2nd in the order from the right side")

        evidence1 = Evidence("University Career")
        evidence1.addRow([Cell("Mike", Header("Name"), [0, 0]), Cell(10, Header("Score"), [0, 1])])
        evidence1.addRow([Cell(9, Header("Score"), [1, 1])])
        evidence1.addRow([Cell(8, Header("Score"), [2, 1])])
        evidence1.addRow([Cell(8, Header("Score"), [3, 1])])
        evidence1.addRow([Cell(4, Header("Score"), [4, 1])])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorRanked = OperatorRanked("Score", "Name")
        check = operatorRanked.checkSemantic(evidence1, self.database)
        self.assertTrue(check, "Ranked Function can be applied")
        self.assertTrue(operatorRanked.value == 10, "Selected value is 10")
        self.assertTrue(operatorRanked.orderType == "desc", "It is close to the right side (ordered asc)")
        self.assertTrue(operatorRanked.pos == 1, "It is the 1st in the order from the right side")

        evidence1 = Evidence("University Career")
        evidence1.addRow([Cell(10, Header("Score"), [0, 1])])
        evidence1.addRow([Cell(9, Header("Score"), [1, 1])])
        evidence1.addRow([Cell(8, Header("Score"), [2, 1])])
        evidence1.addRow([Cell(8, Header("Score"), [3, 1])])
        evidence1.addRow([Cell("Paul", Header("Name"), [4, 0]), Cell(4, Header("Score"), [4, 1])])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorRanked = OperatorRanked("Score", "Name")
        check = operatorRanked.checkSemantic(evidence1, self.database)
        self.assertTrue(check, "Ranked Function can be applied")
        self.assertTrue(operatorRanked.value == 4, "Selected value is 4")
        self.assertTrue(operatorRanked.orderType == "asc", "It is close to the left side (ordered asc)")
        self.assertTrue(operatorRanked.pos == 1, "It is the 1st in the order from the left side")

        evidence1 = Evidence("University Career")
        evidence1.addRow([Cell(10, Header("Score"), [0, 1])])
        evidence1.addRow([Cell(9, Header("Score"), [1, 1])])
        evidence1.addRow([Cell(8, Header("Score"), [2, 1])])
        evidence1.addRow([Cell("Mike", Header("Name"), [3, 0]), Cell(8, Header("Score"), [3, 1])])
        evidence1.addRow([Cell(4, Header("Score"), [4, 1])])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorRanked = OperatorRanked("Score", "Name")
        check = operatorRanked.checkSemantic(evidence1, self.database)
        self.assertTrue(check, "Ranked Function can be applied")
        self.assertTrue(operatorRanked.value == 8, "Selected value is 8")
        self.assertTrue(operatorRanked.orderType == "asc", "It is close to the left side (ordered asc)")
        self.assertTrue(operatorRanked.pos == 2, "It is the 1st in the order from the left side")

        evidence1 = Evidence("University Career")
        evidence1.addRow([Cell(10, Header("Score"), [0, 1])])
        evidence1.addRow([Cell("Anne", Header("Name"), [1, 0]), Cell(9, Header("Score"), [1, 1])])
        evidence1.addRow([Cell(8, Header("Score"), [2, 1])])
        evidence1.addRow([Cell("Mike", Header("Name"), [3, 0]), Cell(8, Header("Score"), [3, 1])])
        evidence1.addRow([Cell(4, Header("Score"), [4, 1])])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorRanked = OperatorRanked("Score", "Name")
        check = operatorRanked.checkSemantic(evidence1, self.database)
        self.assertFalse(check, "Ranked Function cannot be applied due two names selected")

        evidence1 = Evidence("University Career")
        evidence1.addRow([Cell(10, Header("Score"), [0, 1])])
        evidence1.addRow([Cell("Anne", Header("Name"), [1, 0]), Cell(9, Header("Score"), [1, 1])])
        evidence1.addRow([Cell(8, Header("Score"), [2, 1])])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorRanked = OperatorRanked("Score", "Name")
        check = operatorRanked.checkSemantic(evidence1, self.database)
        self.assertFalse(check, "Ranked Function cannot be applied due Score column not selected completely")

    def test_rankedFunctionSimple(self):
        evidence1 = Evidence("University Career")
        evidence1.addRow([Cell("Anne", Header("Name"), [1, 0]), Cell(9, Header("Score"), [1, 1])])
        evidence1.addRow([Cell("Mike", Header("Name"), [0, 0]), Cell(10, Header("Score"), [0, 1])])
        evidence1.addRow([Cell("Albert", Header("Name"), [2, 0]), Cell(8, Header("Score"), [2, 1])])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorRanked = OperatorRankedSimple("Score", "Name")
        check = operatorRanked.checkSemantic(evidence1, self.database)
        self.assertTrue(check, "Ranked Function can be applied")
        self.assertTrue(operatorRanked.value == 9, "Selected value is 9")
        self.assertTrue(operatorRanked.orderType == "desc", "It is close to the right side (ordered asc)")
        self.assertTrue(operatorRanked.pos == 2, "It is the 2nd in the order from the right side")

        evidence1 = Evidence("University Career")
        evidence1.addRow([Cell("Mike", Header("Name"), [0, 0]), Cell(10, Header("Score"), [0, 1])])
        evidence1.addRow([Cell("Anne", Header("Name"), [1, 0]), Cell(9, Header("Score"), [1, 1])])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorRanked = OperatorRankedSimple("Score", "Name")
        check = operatorRanked.checkSemantic(evidence1, self.database)
        self.assertTrue(check, "Ranked Function can be applied")
        self.assertTrue(operatorRanked.value == 10, "Selected value is 10")
        self.assertTrue(operatorRanked.orderType == "desc", "It is close to the right side (ordered asc)")
        self.assertTrue(operatorRanked.pos == 1, "It is the 1st in the order from the right side")

        evidence1 = Evidence("University Career")
        evidence1.addRow([Cell("Paul", Header("Name"), [4, 0]), Cell(4, Header("Score"), [4, 1])])
        evidence1.addRow([Cell("Albert", Header("Name"), [2, 0]), Cell(8, Header("Score"), [2, 1])])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorRanked = OperatorRankedSimple("Score", "Name")
        check = operatorRanked.checkSemantic(evidence1, self.database)
        self.assertTrue(check, "Ranked Function can be applied")
        self.assertTrue(operatorRanked.value == 4, "Selected value is 4")
        self.assertTrue(operatorRanked.orderType == "asc", "It is close to the left side (ordered asc)")
        self.assertTrue(operatorRanked.pos == 1, "It is the 1st in the order from the left side")

        evidence1 = Evidence("University Career")
        evidence1.addRow([Cell("Mike", Header("Name"), [3, 0]), Cell(8, Header("Score"), [3, 1])])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorRanked = OperatorRankedSimple("Score", "Name")
        check = operatorRanked.checkSemantic(evidence1, self.database)
        self.assertTrue(check, "Ranked Function can be applied")
        self.assertTrue(operatorRanked.value == 8, "Selected value is 8")
        self.assertTrue(operatorRanked.orderType == "asc", "It is close to the left side (ordered asc)")
        self.assertTrue(operatorRanked.pos == 2, "It is the 1st in the order from the left side")

        evidence1 = Evidence("University Career")
        evidence1.addRow([Cell(10, Header("Score"), [0, 1])])
        evidence1.addRow([Cell("Anne", Header("Name"), [1, 0]), Cell(9, Header("Score"), [1, 1])])
        evidence1.addRow([Cell(8, Header("Score"), [2, 1])])
        evidence1.addRow([Cell("Mike", Header("Name"), [3, 0]), Cell(8, Header("Score"), [3, 1])])
        evidence1.addRow([Cell(4, Header("Score"), [4, 1])])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorRanked = OperatorRankedSimple("Score", "Name")
        check = operatorRanked.checkSemantic(evidence1, self.database)
        self.assertFalse(check, "Ranked Function cannot be applied due two names selected")

    def test_percentageFunction(self):
        # Name | Score | Exam
        # Mike | 10 | PP
        # Anne | 9 | PP
        # Albert | 8 | PP
        # Mike | 8 | A1
        # Paul | 4 | A2
        evidence1 = Evidence("University Career")
        evidence1.addRow([Cell("Anne", Header("Name"), [1, 0]), Cell(9, Header("Score"), [1, 1])])
        evidence1.addRow([Cell("Paul", Header("Name"), [4, 0]), Cell(4, Header("Score"), [4, 1])])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorPercentage = OperatorPercentage("Score")
        check = operatorPercentage.checkSemantic(evidence1, self.database)
        self.assertTrue(check, "Percentage Function ca be applied")
        operatorPercentage = OperatorPercentage("Name")
        check = operatorPercentage.checkSemantic(evidence1, self.database)
        self.assertFalse(check, "Percentage Function cannot be applied with Name")
        evidence1 = Evidence("University Career")
        evidence1.addRow([Cell("Anne", Header("Name"), [1, 0]), Cell(9, Header("Score"), [1, 1])])
        evidence1.addRow([Cell("Paul", Header("Name"), [4, 0]), Cell(4, Header("Score"), [4, 1])])
        evidence1.addRow([Cell("Mike", Header("Name"), [3, 0]), Cell(8, Header("Score"), [3, 1])])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorPercentage = OperatorPercentage("Score")
        check = operatorPercentage.checkSemantic(evidence1, self.database)
        self.assertFalse(check, "Percentage Function cannot be applied with more than 2 rows")
        evidence1 = Evidence("University Career")
        evidence1.addRow([Cell("Anne", Header("Name"), [1, 0]), Cell(9, Header("Score"), [1, 1])])
        evidence1.build()
        evidence1.inferTypesFromDB(self.database)
        operatorPercentage = OperatorPercentage("Score")
        check = operatorPercentage.checkSemantic(evidence1, self.database)
        self.assertFalse(check, "Percentage Function cannot be applied with 1 row")
