from src.model.IOperator import IOperator


class OperatorLookup(IOperator):

    def __init__(self):
        self.MAX_ROW = 20

    def checkSemantic(self, evidence, database) -> bool:
        if evidence.rowNumber() >= self.MAX_ROW: return False
        #if evidence.singleColumnComplete(): return False
        return True

    def printOperator(self, evidence, database, attributes=None) -> str:
        headerNames = evidence.getHeaderNames()
        if attributes != None: headerNames = attributes
        return "read(" + ",".join(headerNames)+")[*]"

    def __repr__(self):
       return "Lookup"
