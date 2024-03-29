from src.model.RelationalTable import Header, Cell, Evidence, Table, Database
from src import Constants


def checkEvidence(evidence, database, operation):
    if operation in [Constants.OPERATION_LOOKUP, Constants.OPERATION_COMPARISON, Constants.OPERATION_GROUPING]:
        # TODO: check against data? if the evidence do not contain any data from tables?
        #      it is always true?
        return True
    for header in evidence.headers:
        values = evidence.getValuesForAttr(header.name)
        for table in database.tables:
            attribute = table.getAttribute(header)
            if (attribute is not None) and (attribute.type == Constants.NUMERICAL):
                valueInTable = table.getValueForAggregate(attribute.name, operation)
                if (operation in [Constants.OPERATION_MIN, Constants.OPERATION_MAX]) and evidence.isComplete() and (
                        valueInTable in values): return True
                if (operation in [Constants.OPERATION_COUNT]) and evidence.isComplete() and (
                        len(values) <= valueInTable): return True
            if (attribute is not None) and (attribute.type == Constants.CATEGORICAL):
                if (operation in [Constants.OPERATION_COUNT]) and evidence.isComplete():
                    valueInTable = table.getValueForAggregate(attribute.name, operation)
                    return len(values) <= valueInTable
    return False


def checkEvidenceForComparison(evidence, database, operator):
    for header in evidence.headers:
        for table in database.tables:
            attribute = table.getAttribute(header)
            if (attribute is not None) and (attribute.type == Constants.NUMERICAL):
                values = evidence.getValuesForAttr(header.name)
                uniqueValues = set()
                uniqueValues.update(values)
                if (len(uniqueValues) == 1) and (operator == Constants.OPERATOR_SAME): return True
                if (len(uniqueValues) > 1) and (operator in [Constants.OPERATOR_LT, Constants.OPERATOR_GT]): return True
            if (attribute is not None) and (attribute.type == Constants.CATEGORICAL):
                values = evidence.getValuesForAttr(header.name)
                uniqueValues = set()
                uniqueValues.update(values)
                if (len(uniqueValues) == 1) and (operator == Constants.OPERATOR_SAME): return True
    return False


def checkEvidenceForGrouping(evidence, database, operator):
    for header in evidence.headers:
        for table in database.tables:
            attribute = table.getAttribute(header)
            if (attribute is not None) and (attribute.type == Constants.NUMERICAL):
                values = evidence.getValuesForAttr(header.name)
                uniqueValues = set()
                uniqueValues.update(values)
                valuesInColumn = table.getValuesForColumn(header.name)
                setValuesInColumn = set()
                setValuesInColumn.update(valuesInColumn)
                if (len(uniqueValues) == 1) and (operator == Constants.OPERATOR_SAME):
                    value = values[0]
                    valueSize = len(values)
                    countValuesInColumn = valuesInColumn.count(value)
                    if valueSize == countValuesInColumn and evidence.isComplete(): return True, header.name, value
                if (len(uniqueValues) > 1) and (operator == Constants.OPERATOR_GT):
                    minInEvidence = min(values)
                    if len(setValuesInColumn - uniqueValues) > 0:
                        maxInDataExceptEvidence = max(setValuesInColumn - uniqueValues)
                        if (
                                maxInDataExceptEvidence < minInEvidence) and evidence.isComplete(): return True, header.name, maxInDataExceptEvidence
                if (len(uniqueValues) > 1) and (operator == Constants.OPERATOR_LT):
                    maxInEvidence = max(values)
                    if len(setValuesInColumn - uniqueValues) > 0:
                        minInDataExceptEvidence = min(setValuesInColumn - uniqueValues)
                        if (
                                minInDataExceptEvidence > maxInEvidence) and evidence.isComplete(): return True, header.name, minInDataExceptEvidence
            if (attribute is not None) and (attribute.type == Constants.CATEGORICAL):
                values = evidence.getValuesForAttr(header.name)
                uniqueValues = set()
                uniqueValues.update(values)
                if (len(uniqueValues) == 1) and (operator == Constants.OPERATOR_SAME):
                    value = values[0]
                    valueSize = len(values)
                    valuesInColumn = table.getValuesForColumn(header.name)
                    countValuesInColumn = valuesInColumn.count(value)
                    if valueSize == countValuesInColumn and evidence.isComplete(): return True, header.name, value
    return False, None, None
