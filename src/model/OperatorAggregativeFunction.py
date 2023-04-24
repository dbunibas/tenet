from src import Constants
from src.model.IOperator import IOperator
from src.model.OperatorFilter import OperatorFilter


class OperatorAggregativeFunction(IOperator):

    def __init__(self, attribute, function):
        self.attribute = attribute
        self.function = function
        self.attributeFilter = None
        self.comparator = None
        self.operatorFilter = None
        self.value = None

    def setFilter(self, attributeFilter, comparator):
        self.attributeFilter = attributeFilter
        self.comparator = comparator
        self.operatorFilter = OperatorFilter(self.attributeFilter, self.comparator)

    def isWithFilter(self):
        return self.operatorFilter is not None

    def checkSemantic(self, evidence, database) -> bool:
        header = evidence.getHeaderByName(self.attribute)
        valuesForAttr = evidence.getValuesForAttr(self.attribute)
        table = database.getTable(evidence.tableName, self.attribute)
        valuesForColumnInTable = table.getValuesForColumn(self.attribute)
        if self.operatorFilter is not None:
            ## Check if there is a Filter
            if not self.operatorFilter.checkSemantic(evidence, database): return False
            valuesForFilter = evidence.getValuesForAttr(self.attributeFilter)
            if len(valuesForAttr) != len(valuesForFilter): return False
        else:
            ## Check if the whole column is selected
            if len(valuesForAttr) != len(valuesForColumnInTable): return False  ## Evidence should be the same as the original table

        #sameValuesInEvidence = all(elem in valuesForAttr for elem in valuesForColumnInTable)
        #print("Values for attr in evidence: ", valuesForAttr)
        #print("Values for attr in table: ", valuesForColumnInTable)
        #print("*** LOG- SAME VALUES IN EVIDENCE: ", sameValuesInEvidence, self.attribute, self.function, self.comparator)
        #if not sameValuesInEvidence: return False  ## Evidence should contain the same values as the original table
        if header.type == Constants.CATEGORICAL and self.function in [Constants.OPERATION_SUM, Constants.OPERATION_AVG]: return False
        valuesForAttr = evidence.getValuesForAttr(self.attribute)
        self.value = self.computeValue(valuesForAttr)
        return True

        # if self.operatorFilter is None:
        #     if len(valuesForAttr) != len(valuesForColumnInTable): return False  ## Evidence should be the same as the original table
        #     sameValuesInEvidence = all(elem in valuesForAttr for elem in valuesForColumnInTable)
        #     if not sameValuesInEvidence: return False  ## Evidence should contain the same values as the original table
        #     if header.type == Constants.CATEGORICAL and self.function in [Constants.OPERATION_SUM, Constants.OPERATION_AVG]: return False
        #     return True
        # else:
        #     ## Check if there is a Filter
        #     if not self.operatorFilter.checkSemantic(evidence, database): return False
        #     sameValuesInEvidence = all(elem in valuesForAttr for elem in valuesForColumnInTable)
        #     if not sameValuesInEvidence: return False  ## Evidence should contain the same values as the original table
        #     if header.type == Constants.CATEGORICAL and self.function in [Constants.OPERATION_SUM, Constants.OPERATION_AVG]: return False
        #     return True



    def printOperator(self, evidence, database, attributes=None) -> str:
        #compute(avg,Kilometers)=19000
        sValue = ""
        prefix = ""
        if self.value is not None:
            sValue = "=" + str(self.value)
        if self.operatorFilter is not None:
            prefix = self.operatorFilter.printOperator(evidence, database)+","
        return prefix+"compute(" + self.function + "," + self.attribute.lower() +  ")" +sValue

    def computeValue(self, values):
        if self.function == Constants.OPERATION_SUM:
            return sum(values)
        if self.function == Constants.OPERATION_AVG:
            return (sum(values)+0.0) / len(values)
        if self.function == Constants.OPERATION_COUNT:
            return len(values)
        print("*** ERROR." + self.function + " not defined")
        return None

    def __repr__(self):
        sName =  "AggregativeFunction - " + self.function + " - " + self.attribute
        if self.attributeFilter is not None:
            sName += "-Filter on: " + self.attributeFilter + " with: " + str(self.operatorFilter)
        return sName

