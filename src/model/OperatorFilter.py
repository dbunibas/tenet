from src import Constants
from src.model.IOperator import IOperator
from collections import Counter


class OperatorFilter(IOperator):

    def __init__(self, attribute, comparator):
        self.attribute = attribute
        self.comparator = comparator
        self.value = None

    def checkSemantic(self, evidence, database) -> bool:
        if evidence.rowNumber() < 2: return False
        if not evidence.isCompleteForAttribute(self.attribute): return False
        header = evidence.getHeaderByName(self.attribute)
        valuesForAttr = evidence.getValuesForAttr(self.attribute)
        uniqueValues = set()
        uniqueValues.update(valuesForAttr)
        table = database.getTable(evidence.tableName, self.attribute)
        if header.type == Constants.NUMERICAL:
            valuesForColumnInTable = table.getValuesForColumn(self.attribute)
            setValuesInColumn = set()
            setValuesInColumn.update(valuesForColumnInTable)
            if (len(uniqueValues) == 1) and (self.comparator == Constants.OPERATOR_SAME):
                value = valuesForAttr[0]
                valueSize = len(valuesForAttr)
                countValuesInColumn = valuesForColumnInTable.count(value)
                if valueSize == countValuesInColumn:
                    self.value = value
                    return True
            if (len(uniqueValues) > 1) and (self.comparator == Constants.OPERATOR_GT):
                minInEvidence = min(valuesForAttr)
                diff = self.difference(valuesForColumnInTable, valuesForAttr)
                if len(diff) > 0:
                    maxInDataExceptEvidence = max(diff)
                    if (maxInDataExceptEvidence < minInEvidence):
                        self.value = maxInDataExceptEvidence
                        return True
            if (len(uniqueValues) > 1) and (self.comparator == Constants.OPERATOR_LT):
                maxInEvidence = max(valuesForAttr)
                diff = self.difference(valuesForColumnInTable, valuesForAttr)
                if len(diff) > 0:
                    minInDataExceptEvidence = min(diff)
                    if (minInDataExceptEvidence > maxInEvidence):
                        self.value = minInDataExceptEvidence
                        return True
            return False
        else:
            if self.comparator in [Constants.OPERATOR_LT, Constants.OPERATOR_GT]: return False
            if len(uniqueValues) != 1: return False  ## TODO: we assume that we have only one group
            value = valuesForAttr[0]
            table = database.getTable(evidence.tableName, self.attribute)
            valuesForColumnInTable = table.getValuesForColumn(self.attribute)
            occurrencesInTable = valuesForColumnInTable.count(value)
            if len(valuesForAttr) < occurrencesInTable: return False ## Evidence cannot be bigger than the original table
            self.value = value
            return True

    def printOperator(self, evidence, database, attributes=None) -> str:
        sValue = ""
        if self.value is not None:
            sValue = self.comparator+str(self.value)
        return "filter(" + self.attribute + ")"+sValue

    def __repr__(self):
       return "Filter on" + self.attribute + "with " + self.comparator

    def difference(self, l1, l2):
        freq1 = Counter(l1)
        freq2 = Counter(l2)
        result = set()
        for key, count in freq1.items():
            count2 = freq2.get(key)
            if count2 is None: result.add(key)
            else:
                if count2 < count: result.add(key)
        return result


