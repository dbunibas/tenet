from src import Constants
from src.model.OperatorAggregativeFunction import OperatorAggregativeFunction
from src.model.OperatorComparison import OperatorComparison
from src.model.OperatorFilter import OperatorFilter
from src.model.OperatorLookup import OperatorLookup
from src.model.OperatorMinMax import OperatorMinMax


class OperatorFinder:
    def __init__(self, evidence, database, operations, comparisons):
        self.evidence = evidence
        self.database = database
        self.operations = operations
        self.comparisons = comparisons
        self.allowedOperations = []
        self.operators = []

    def exploreAll(self):
        self.buildOperators()
        for operator in self.operators:
            try:
                if operator.checkSemantic(self.evidence, self.database): self.allowedOperations.append(operator)
            except Exception:
                # print("Exception with: " + str(operator))
                pass
                # TODO: log exceptions
        ## TODO: compose allowedOperations?

    def buildOperators(self):
        for operation in self.operations:
            if operation == Constants.OPERATION_LOOKUP:
                operation = OperatorLookup()
                self.operators.append(operation)
            for attribute in self.evidence.getHeaderNames():
                operators = self.createExploratoryOperators(operation, attribute)
                if len(operators) > 0: self.operators += operators

    def createExploratoryOperators(self, operation, attribute):
        operators = []
        if operation == Constants.OPERATION_COMPARISON:
            for comparator in self.comparisons:
                operator = OperatorComparison(attribute, comparator)
                operators.append(operator)
        if operation == Constants.OPERATION_FILTER:
            for comparator in self.comparisons:
                operator = OperatorFilter(attribute, comparator)
                operators.append(operator)
        if operation in [Constants.OPERATION_MIN, Constants.OPERATION_MAX]:
            operator = OperatorMinMax(attribute, operation)
            operators.append(operator)
        if operation in [Constants.OPERATION_COUNT, Constants.OPERATION_SUM, Constants.OPERATION_AVG]:
            ## WE CANNOT GENERATE IT UNLESS WE TRY ALL THE POSSIBLE COMBINATIONS PAIRWISE ATTRIBUTES
            operator = OperatorAggregativeFunction(attribute, operation)
            operators.append(operator)
            for filterAttribute in self.evidence.getHeaderNames():
                if attribute != filterAttribute:
                    for comparator in self.comparisons:
                        operator = OperatorAggregativeFunction(attribute, operation)
                        operator.setFilter(filterAttribute, comparator)
                        operators.append(operator)
        return operators