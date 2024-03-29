from src import Constants
from src.model.IOperator import IOperator
from src.textGeneration import TextUtils


class OperatorComparison(IOperator):

    def __init__(self, attribute, comparator):
        self.attribute = attribute
        self.comparator = comparator

    def checkSemantic(self, evidence, database) -> bool:
        if evidence.rowNumber() == 1: return False
        valuesForAttr = evidence.getValuesForAttr(self.attribute)
        if len(valuesForAttr) == 1: return False
        if len(valuesForAttr) < evidence.rowNumber(): return False
        header = evidence.getHeaderByName(self.attribute)
        if header is None:
            print("*** ERROR: unable to find ", self.attribute + "in the evidence.")
            print("*** Headers in evidence:", evidence.getHeaderNames())
            return False
        if header.type == Constants.CATEGORICAL and self.comparator != Constants.OPERATOR_SAME: return False
        uniqueValues = set()
        uniqueValues.update(valuesForAttr)
        if header.type == Constants.CATEGORICAL and self.comparator == Constants.OPERATOR_SAME and len(
            uniqueValues) > 1: return False
        if header.type == Constants.NUMERICAL and self.comparator == Constants.OPERATOR_SAME and len(
            uniqueValues) > 1: return False
        return True

    def printOperator(self, evidence, database, attributes=None) -> str:
        # keyAttribute = evidence.getKey()
        # attrList = [keyAttribute, self.attribute]
        attrList = evidence.getHeaderNames()
        if attributes is not None:
            attrList = attributes
        attrListLower = TextUtils.all_lower(attrList)
        readOp = "read(" + ",".join(attrListLower) + ")[*]"
        # return readOp + ", compare("+ keyAttribute.lower() + "," + self.comparator + "," + self.attribute.lower() + ")"
        return readOp + ", compare(" + self.comparator + "," + self.attribute.lower() + ")"

    def getScore(self):
        return 0.1

    def __repr__(self):
        sName = "Comparison - " + self.comparator + " on " + self.attribute
        return sName

    def getTenetName(self):
        return Constants.OPERATION_COMPARISON
