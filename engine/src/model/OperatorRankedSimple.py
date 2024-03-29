from src import Constants
from src.model.IOperator import IOperator
from bisect import bisect
from random import randrange


class OperatorRankedSimple(IOperator):

    def __init__(self, attributeRank, subjectAttribute):
        self.attributeRank = attributeRank
        self.subjectAttribute = subjectAttribute
        self.pos = None
        self.orderType = None
        self.value = None

    def checkSemantic(self, evidence, database) -> bool:
        header = evidence.getHeaderByName(self.attributeRank)
        if header is None:
            print("*** ERROR: unable to find ", self.attributeRank + "in the evidence.")
            print("*** Headers in evidence:", evidence.getHeaderNames())
            return False
        if header.type == Constants.CATEGORICAL: return False
        headerSubj = evidence.getHeaderByName(self.subjectAttribute)
        if headerSubj is None:
            print("*** ERROR: unable to find ", self.subjectAttribute + "in the evidence.")
            print("*** Headers in evidence:", evidence.getHeaderNames())
            return False
        if headerSubj.type == Constants.NUMERICAL: return False
        valuesForAttr = evidence.getValuesForAttr(self.attributeRank)
        valuesForSubj = evidence.getValuesForAttr(self.subjectAttribute)
        if len(valuesForAttr) != len(valuesForSubj): return False
        # index = randrange(len(valuesForAttr))
        index = 0
        valueForAttr = valuesForAttr[index]
        table = database.getTable(evidence.tableName, self.attributeRank)
        valuesForColumnInTable = table.getValuesForColumn(self.attributeRank)
        sameValuesInEvidence = all(elem in valuesForAttr for elem in valuesForColumnInTable)
        if valueForAttr not in valuesForColumnInTable: return False  ## Evidence should contain the same value as the original table
        subjectCells = evidence.getCellsForAttribute(self.subjectAttribute)
        subjectCell = subjectCells[index]
        self.value = valueForAttr
        self.pos, self.orderType = self.findValueInRankedList(self.value, valuesForColumnInTable)
        return True

    def printOperator(self, evidence, database, attributes=None) -> str:
        ## TODO: define the sintax for the operator
        sValue = ""
        if self.value is not None:
            sValue = "=" + str(self.value)
        return "ranked(" + str(self.pos) + "," + self.orderType + "," + self.attributeRank.lower() + ")" + sValue

    def findValueInRankedList(self, valueToFind, valuesInColumn):
        distincValues = list(set(valuesInColumn))
        distincValues.sort()
        pos = bisect(distincValues, valueToFind)
        half = round(len(distincValues) / 2)
        orderType = "asc"
        if pos > half:
            orderType = "desc"
            pos = len(distincValues) - pos + 1
        return pos, orderType

    def getScore(self):
        return 1.5

    def __repr__(self):
        # return "ranked " + self.orderType + " on " + self.attributeRank + " with pos " + str(self.pos)
        return "ranked(" + self.attributeRank.lower() + "," + self.subjectAttribute.lower() + ")"

    def getTenetName(self):
        return Constants.OPERATION_RANKED
