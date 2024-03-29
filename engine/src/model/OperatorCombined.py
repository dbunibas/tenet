from src import Constants
from src.model.IOperator import IOperator


class OperatorCombined(IOperator):

    def __init__(self, operators):
        self.operators = operators

    def checkSemantic(self, evidence, database) -> bool:
        for op in self.operators:
            if not op.checkSemantic(evidence, database): return False
        if self.containsSameOperators(): return False
        return True

    def printOperator(self, evidence, database, attributes=None) -> str:
        operatorsStrings = []
        for op in self.operators:
            operatorsStrings.append(op.printOperator(evidence, database, attributes))
        sOperator = ", ".join(operatorsStrings)
        return sOperator

    def getScore(self):
        score = 0.0
        for op in self.operators:
            score += op.getScore()
        return score

    def containsSameOperators(self):
        occurrences = {}
        for op in self.operators:
            count = 1
            if op.getTenetName() in occurrences:
                # if op.__class__.__name__ in occurrences:
                # count = occurrences[op.__class__.__name__]
                count = occurrences[op.getTenetName]
                count += 1
            # occurrences[op.__class__.__name__] = count
            occurrences[op.getTenetName] = count
        for k, v in occurrences.items():
            if v > 1: return True
        return False

    def __repr__(self):
        operatorsStrings = []
        for op in self.operators:
            operatorsStrings.append(op)
        sName = "CombinedOperator: " + ", ".join(operatorsStrings)
        return sName

    def getTenetName(self):
        return Constants.OPERATION_COMBINED
