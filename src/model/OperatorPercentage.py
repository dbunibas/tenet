from src import Constants
from src.model.IOperator import IOperator
from src.textGeneration import TextUtils


class OperatorPercentage(IOperator):

    def __init__(self, attribute):
        self.attribute = attribute

    def checkSemantic(self, evidence, database) -> bool:
        if evidence.rowNumber() != 2: return False ## only pairwise comparisons
        valuesForAttr = evidence.getValuesForAttr(self.attribute)
        if len(valuesForAttr) != 2: return False ## there should be 2 values
        header = evidence.getHeaderByName(self.attribute)
        if header is None:
            print("*** ERROR: unable to find ", self.attribute + "in the evidence.")
            print("*** Headers in evidence:", evidence.getHeaderNames())
            return False
        if header.type == Constants.CATEGORICAL: return False ## percentage could be applied only with numerical attrs
        ## check values with comparator
        value1 = valuesForAttr[0]
        value2 = valuesForAttr[1]
        if value1 == value2: return False
        try:
            v1Val = float(value1)
            v2Val = float(value2)
        except:
            return False
        if float(value1) == 0: return False ## we can't divide by zero
        return True

    def printOperator(self, evidence, database, attributes=None) -> str:
        valuesForAttr = evidence.getValuesForAttr(self.attribute)
        value1 = float(valuesForAttr[0])
        value2 = float(valuesForAttr[1])
        percentage = ((value2 - value1) / abs(value1)) * 100
        comparator = ">"
        if percentage < 0: comparator = "<"
        attrList = evidence.getHeaderNames()
        if attributes is not None:
            attrList = attributes
        attrListLower = TextUtils.all_lower(attrList)
        readOp = "read(" + ",".join(attrListLower) + ")[*]"
        sValue = ""
        if percentage is not None:
            formatPercentage = "{:.2f}".format(percentage)
            sValue = "=" + str(formatPercentage) + "%"
        return readOp + ", percentage("+ self.attribute.lower()+"," + comparator + ")" + sValue

    def getScore(self):
        return 0.5

    def __repr__(self):
        return  "Percentage on: " + self.attribute

    def getTenetName(self):
        return Constants.OPERATION_PERCENTAGE