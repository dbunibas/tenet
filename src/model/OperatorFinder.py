from src import Constants
from src.LoggedDecorators import timed
from src.model.OperatorAggregativeFunction import OperatorAggregativeFunction
from src.model.OperatorCombined import OperatorCombined
from src.model.OperatorComparison import OperatorComparison
from src.model.OperatorFilter import OperatorFilter
from src.model.OperatorLookup import OperatorLookup
from src.model.OperatorMinMax import OperatorMinMax
from src.model.OperatorPercentage import OperatorPercentage
from src.model.OperatorRanked import OperatorRanked
from src.model.OperatorRankedSimple import OperatorRankedSimple
import traceback
import itertools
import logging
import time

logger = logging.getLogger(__name__)

class OperatorFinder:
    def __init__(self, evidence, database, operations, comparisons):
        self.evidence = evidence
        self.database = database
        self.operations = operations
        self.comparisons = comparisons
        self.allowedOperations = []
        self.operators = []
        self.statistics = None

    def setStatistics(self, statisticsObj):
        self.statistics = statisticsObj

    #@timed
    def exploreAll(self, composedOperations=False):
        self.buildOperators()
        operationsForCombination = []
        #print("Operators to explore: ", len(self.operators))
        counterChecked = 0
        for operator in self.operators:
            try:
                start = time.time();
                #print("Try:", operator)
                check = operator.checkSemantic(self.evidence, self.database)
                if check:
                    self.allowedOperations.append(operator)
                    if operator.__class__.__name__ in [OperatorAggregativeFunction.__name__, OperatorMinMax.__name__,
                                                       OperatorFilter.__name__, OperatorComparison.__name__]:
                        operationsForCombination.append(operator)
                    self.statistics.addOrUpdate("Valid_" + operator.__class__.__name__, 1)
                    counterChecked += 1
                end = time.time()
                if self.statistics is not None:
                    self.statistics.addOrUpdate("Checking_" + operator.__class__.__name__, (end-start))
                    self.statistics.addOrUpdate("Tested_" + operator.__class__.__name__, 1)
                #print(operator.__class__.__name__, "{:.10f}".format(end - start), check, sep="\t")
            except Exception:
                #pass
                #logger.error("Exception with: " + str(operator))
                #traceback.print_exc()
                pass
        #print("Passed", counterChecked, "over", len(self.operators))
        if composedOperations:
            operationsToAdd = []
            #for size in range(2, len(self.allowedOperations) + 1):
            for size in range(2, 4): ## limit compositions
                #for combination in itertools.permutations(operationsForCombination, size):
                for combination in itertools.combinations(operationsForCombination, size):
                    operator = OperatorCombined(list(combination))
                    if operator.checkSemantic(self.evidence, self.database): operationsToAdd.append(operator)
            self.allowedOperations += operationsToAdd


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
        if operation in [Constants.OPERATION_PERCENTAGE]:
            operator = OperatorPercentage(attribute)
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
        if operation in [Constants.OPERATION_RANKED]:
            for subjAttribute in self.evidence.getHeaderNames():
                if attribute != subjAttribute:
                    #operator = OperatorRanked(attribute, subjAttribute)
                    operator = OperatorRankedSimple(attribute, subjAttribute)
                    operators.append(operator)
        return operators
