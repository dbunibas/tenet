from src import Constants
from src.model.IOperator import IOperator
from bisect import bisect


class OperatorRanked(IOperator):

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
        valuesForAttr = evidence.getValuesForAttr(self.attributeRank)
        table = database.getTable(evidence.tableName, self.attributeRank)
        valuesForColumnInTable = table.getValuesForColumn(self.attributeRank)
        if len(valuesForAttr) != len(valuesForColumnInTable): return False ## Evidence should be the same as the original table
        sameValuesInEvidence = all(elem in valuesForAttr for elem in valuesForColumnInTable)
        if not sameValuesInEvidence: return False ## Evidence should contain the same values as the original table
        subjectCells = evidence.getCellsForAttribute(self.subjectAttribute)
        if len(subjectCells) > 1: return False ## Selected values for the subject should be 1
        subjectCell = subjectCells[0]
        row = subjectCell.getRowPos()
        self.value = evidence.getCellByRowAndAttr(row, self.attributeRank).value
        self.pos, self.orderType = self.findValueInRankedList(self.value, valuesForColumnInTable)
        return True

    def printOperator(self, evidence, database, attributes=None) -> str:
        ## TODO: define the sintax for the operator
        sValue = ""
        if self.value is not None:
            sValue = "=" + str(self.value)
        return "ranked(" + str(self.pos) + "," + self.orderType + ","+ self.attributeRank.lower() + ")" + sValue

    def findValueInRankedList(self, valueToFind, valuesInColumn):
        distincValues = list(set(valuesInColumn))
        distincValues.sort()
        pos = bisect(distincValues, valueToFind)
        half = round(len(distincValues)/2)
        orderType = "asc"
        if pos > half:
            orderType = "desc"
            pos = len(distincValues) - pos + 1
        return pos, orderType

    def getScore(self):
        return 15.0

    def __repr__(self):
        #return "ranked " + self.orderType + " on " + self.attributeRank + " with pos " + str(self.pos)
        return "ranked(" + self.attributeRank.lower() + "," + self.subjectAttribute.lower() + ")"