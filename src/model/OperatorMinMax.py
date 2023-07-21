from src import Constants
from src.model.IOperator import IOperator
import time


class OperatorMinMax(IOperator):

    def __init__(self, attribute, function):
        self.attribute = attribute
        self.function = function
        self.value = None

    def checkSemantic(self, evidence, database) -> bool:
        header = evidence.getHeaderByName(self.attribute)
        if header is None:
            print("*** ERROR: unable to find ", self.attribute + "in the evidence.")
            print("*** Headers in evidence:", evidence.getHeaderNames())
            return False
        if header.type == Constants.CATEGORICAL: return False
        valuesForAttr = evidence.getValuesForAttr(self.attribute)
        table = database.getTable(evidence.tableName, self.attribute)
        valuesForColumnInTable = table.getValuesForColumn(self.attribute)
        if len(valuesForAttr) != len(valuesForColumnInTable): return False ## Evidence should be the same as the original table
        sameValuesInEvidence = all(elem in valuesForAttr for elem in valuesForColumnInTable)
        if not sameValuesInEvidence: return False ## Evidence should contain the same values as the original table
        if self.function == Constants.OPERATION_MIN:
            minInTable = table.getValueForAggregate(self.attribute, Constants.OPERATION_MIN)
            if minInTable not in valuesForAttr: return False
            self.value = minInTable
        if self.function == Constants.OPERATION_MAX:
            maxInTable = table.getValueForAggregate(self.attribute, Constants.OPERATION_MAX)
            if maxInTable not in valuesForAttr: return False
            self.value = maxInTable
        return True

    def printOperator(self, evidence, database, attributes=None) -> str:
        sValue = ""
        if self.value is not None:
            sValue = "=" + str(self.value)
        return "compute(" + self.function +","+ self.attribute.lower() + ")" + sValue

    def getScore(self):
        return 10.0

    def __repr__(self):
       return self.function + " on " + self.attribute

    def getTenetName(self):
        return self.function