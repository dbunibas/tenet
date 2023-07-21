from src.LoggedDecorators import timed
from src.model.ISearchStrategy import ISearchStrategy
import random
import collections

from src.model.RelationalTable import Evidence


class ColdSearch(ISearchStrategy):

    def __init__(self):
        super().__init__()
        self.seed = None
        self.maxCellsToPick = None
        self.maxAttempts = 10

    def setSeed(self, seed):
        self.seed = seed
        random.seed(seed)

    def setMaxCellsToPick(self, maxCellsToPick):
        self.maxCellsToPick = maxCellsToPick

    #@timed
    def findEvidences(self, table, numExamples, evidence=None):
        evidences = []
        counterWhile = 0
        maxAttemptWhile = numExamples * 10
        evidencesTuple = []
        while True:
            randomEvidence = self.pickEvidence(table, evidencesTuple)
            if not self.isInGenerated(randomEvidence, evidencesTuple):
                evidencesTuple.append(randomEvidence)
            if len(evidencesTuple) == numExamples: break
            counterWhile += 1
            if counterWhile >= maxAttemptWhile: break
        for evTupleList in evidencesTuple:
            ev = self.toEvidence(table, evTupleList)
            evidences.append(ev)
        return evidences

    def pickEvidence(self, table, generatedEvidences):
        colNumber = len(table.schema)
        rowNumber = len(table.rows)
        cols = range(0, colNumber)
        rows = range(0, rowNumber)
        cellsToPick = random.choice(range(1, colNumber * rowNumber))
        if self.maxCellsToPick is not None:
            cellsToPick = self.maxCellsToPick
        evidenceList = []
        for i in range(0, cellsToPick):
            col = random.choice(cols)
            row = random.choice(rows)
            t = (row, col)
            counterEvidence = 0
            while (t in evidenceList) and (counterEvidence < self.maxAttempts):
                col = random.choice(cols)
                row = random.choice(rows)
                t = (row, col)
                counterEvidence += 1
            if counterEvidence < self.maxAttempts and t not in evidenceList:
                evidenceList.append(t)
        return evidenceList


    def isInGenerated(self, evidence, evidences):
        for e in evidences:
            if self.equalsEvidence(e, evidence): return True
        return False

    def equalsEvidence(self, ev1, ev2):
        return collections.Counter(ev1) == collections.Counter(ev2)

    def toEvidence(self, table, evTupleList):
        evidence = Evidence(table.tableName)
        prevRow = -1
        currentRowList = []
        #print(sorted(evTupleList))
        for row, col in sorted(evTupleList):
            if row != prevRow:
                if len(currentRowList) > 0:
                    evidence.addRow(currentRowList)
                currentRowList = []
            cell = table.getCellByPos(row, col)
            cell.setPos([row, col])
            currentRowList.append(cell)
            prevRow = row
        if len(currentRowList) > 0:
            evidence.addRow(currentRowList)
        evidence.build()
        return evidence
