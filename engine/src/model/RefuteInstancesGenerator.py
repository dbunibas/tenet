import random
import copy
import editdistance

from src import Constants
from src.LoggedDecorators import timed
from src.Utils import customDeepCopy
from src.model.RelationalTable import Cell
from src.textGeneration.FlanT5LM import FlanT5LM
import time


class RefuteInstancesGenerator:

    def __init__(self):
        self.seed = None
        self.attemptsForCol = 10
        self.attemptsForRowGeneration = 10
        self.outOfRange = 2
        self.maxExamplesForLM = 5  ## bigger is the number bigger is the time of the generation of one single cell
        self.lm = None

    def setSeed(self, seed):
        self.seed = seed
        random.seed(seed)

    def setLM(self, lm):
        self.lm = lm

    # @timed
    def useLM(self):
        if self.lm is None:
            start_time = time.time()
            self.lm = FlanT5LM()
            end_time = time.time()
            # print("Loaded in (s): ", (end_time-start_time))

    # @timed
    def generateInstanceForRefuteBigTables(self, table, addRows, rowsToAdd, removeRows, rowsToRemove, strategy,
                                           evidenceSel, evidences=None):
        refuteInstance = customDeepCopy(table)
        start = time.time()
        if rowsToAdd < 2 or removeRows:
            print("Warning. This configuration will not broke max or min values")
        if addRows and removeRows:
            print("Error. Cannot generate an instances with add and remove rows together")
            return None
        if rowsToAdd:
            valuesForColumns = table.toDict()
            if rowsToAdd == 1:
                refuteInstance = self.addTupleBigTable(refuteInstance, 1, strategy, Constants.STRATEGY_CHANGE_MIN,
                                                       valuesForColumns)
            elif rowsToAdd > 1:
                refuteInstance = self.addTupleBigTable(refuteInstance, 1, strategy, Constants.STRATEGY_CHANGE_MIN,
                                                       valuesForColumns)
                refuteInstance = self.addTupleBigTable(refuteInstance, 1, strategy, Constants.STRATEGY_CHANGE_MAX,
                                                       valuesForColumns)
                refuteInstance = self.addTupleBigTable(refuteInstance, rowsToAdd - 2, strategy, "", valuesForColumns)
        elif rowsToRemove:
            refuteInstance = self.removeTuple(refuteInstance, rowsToRemove)
        end = time.time()
        # print("Add/Remove tuples (s):", (end - start))
        if refuteInstance is not None:
            # print("*** REFUTE-INSTANCE-GENERATOR: shuffle")
            attrFromEvidences = None
            if evidences is not None and len(evidences) > 0:
                attrFromEvidences = []
                for e in evidences:
                    headerInE = e.headers
                    for h in headerInE:
                        if h not in attrFromEvidences: attrFromEvidences.append(h)
            start = time.time()
            refuteInstance, _ = self.shuffleInstanceBigTable(refuteInstance, evidenceSel,
                                                             attrFromEvidences=attrFromEvidences)
            # print("*** REFUTE-INSTANCE-GENERATOR: end shuffle")
            end = time.time()
            # print("Shuffle:", (end - start))
        if refuteInstance is not None:
            # print("*** REFUTE-INSTANCE-GENERATOR: remove same rows")
            start = time.time()
            refuteInstance = self.removeSameRowsBigTable(table,
                                                         refuteInstance)  ## check if there are identical rows in both instances
            # print("*** REFUTE-INSTANCE-GENERATOR: end remove same rows")
            end = time.time()
            # print("Remove same rows:", (end - start))
        return refuteInstance

    # @timed
    def generateInstanceForRefute(self, table, addRows, rowsToAdd, removeRows, rowsToRemove, strategy, evidenceSel):
        # print("Copy instance")
        start = time.time()
        refuteInstance = customDeepCopy(table)
        end = time.time()
        # print("Copy time (s):", (end-start))
        if rowsToAdd < 2 or removeRows:
            print("Warning. This configuration will not broke max or min values")
        if addRows and removeRows:
            print("Error. Cannot generate an instances with add and remove rows together")
            return None
        start = time.time()
        # print("Start Add/Remove")
        if rowsToAdd:
            valuesForColumns = table.toDict()
            if rowsToAdd == 1:
                refuteInstance = self.addTuple(refuteInstance, 1, strategy, Constants.STRATEGY_CHANGE_MIN,
                                               valuesForColumns)
            elif rowsToAdd > 1:
                refuteInstance = self.addTuple(refuteInstance, 1, strategy, Constants.STRATEGY_CHANGE_MIN,
                                               valuesForColumns)
                refuteInstance = self.addTuple(refuteInstance, 1, strategy, Constants.STRATEGY_CHANGE_MAX,
                                               valuesForColumns)
                refuteInstance = self.addTuple(refuteInstance, rowsToAdd - 2, strategy, "", valuesForColumns)
        elif rowsToRemove:
            refuteInstance = self.removeTuple(refuteInstance, rowsToRemove)
        end = time.time()
        # print("Add/Remove tuples (s):", (end-start))
        if refuteInstance is not None:
            # print("*** REFUTE-INSTANCE-GENERATOR: shuffle")
            start = time.time()
            refuteInstance, _ = self.shuffleInstance(refuteInstance, evidenceSel)
            # print("*** REFUTE-INSTANCE-GENERATOR: end shuffle")
            end = time.time()
            # print("Shuffle:", (end - start))
        if refuteInstance is not None:
            # print("*** REFUTE-INSTANCE-GENERATOR: remove same rows")
            start = time.time()
            refuteInstance = self.removeSameRows(table,
                                                 refuteInstance)  ## check if there are identical rows in both instances
            # print("*** REFUTE-INSTANCE-GENERATOR: end remove same rows")
            end = time.time()
            # print("Remove same rows:", (end - start))
        return refuteInstance

    # @timed
    def shuffleInstanceBigTable(self, table, evidenceSel, attrFromEvidences=None):
        # refuteInstance = customDeepCopy(table)
        refuteInstance = table
        attrsShuffle = []
        if attrFromEvidences is not None:
            attrsShuffle = attrFromEvidences
        else:
            if evidenceSel is None:
                attrsShuffle = refuteInstance.schema
            else:
                attrsShuffle = evidenceSel.headers
        for header in attrsShuffle:
            cellsForAttr = refuteInstance.getCellsByHeader(header)
            # originalCellsForAttr = refuteInstance.getCellsByHeader(header)
            random.shuffle(cellsForAttr)
            # originalRowIndex = self.getRowIndexFromCells(cellsForAttr)
            refuteInstance = self.updateValuesInColumn(refuteInstance, header, cellsForAttr)
            # cellsForAttrShuffled = refuteInstance.getCellsByHeader(header)
            # differences = self.countDifferences(originalCellsForAttr, cellsForAttrShuffled)
        return refuteInstance, None

    def shuffleInstance(self, table, evidenceSel):
        refuteInstance = customDeepCopy(table)
        shuffled = 0
        colToShuffle = int(len(refuteInstance.schema) / 2)
        originalOrderForCol = {}
        pickedAttr = set()
        rowNumber = len(refuteInstance.rows)
        for i in range(0, colToShuffle):
            randomAttr = None
            if evidenceSel is None:
                randomAttr = random.choice(refuteInstance.schema)
            else:
                randomAttr = random.choice(evidenceSel.headers)
            attempt = 0
            while (self.emptyCol(refuteInstance.getCellsByHeader(randomAttr)) or (
                    (len(pickedAttr) > 1) and (randomAttr in pickedAttr))) and attempt < self.attemptsForCol:
                if evidenceSel is None:
                    randomAttr = random.choice(refuteInstance.schema - list(pickedAttr))
                else:
                    randomAttr = random.choice(evidenceSel.headers - list(pickedAttr))
                attempt += 1
            if attempt == self.attemptsForCol: break
            # print("Picked attr to shuffle:", randomAttr)
            # print("Visited attrs:", pickedAttr)
            attempt = 0
            prevRefuteInstance = customDeepCopy(refuteInstance)
            while attempt < self.attemptsForCol:
                # print("Shuffle attempt:", attempt)
                cellsForAttr = refuteInstance.getCellsByHeader(randomAttr)
                # print("*** Cells before shuffle:", cellsForAttr)
                originalCellsForAttr = refuteInstance.getCellsByHeader(randomAttr)
                random.shuffle(cellsForAttr)
                # print("*** Cells after shuffle:", cellsForAttr)
                originalRowIndex = self.getRowIndexFromCells(cellsForAttr)
                refuteInstance = self.updateValuesInColumn(refuteInstance, randomAttr, cellsForAttr)
                cellsForAttrShuffled = refuteInstance.getCellsByHeader(randomAttr)
                differences = self.countDifferences(originalCellsForAttr, cellsForAttrShuffled)
                # print("Differences: ",differences, "on", rowNumber)
                if (rowNumber < 50 and differences >= rowNumber / 2) or (
                        differences > rowNumber * 0.05):  # the half of the values are shuffled or 5% in bigger tables
                    originalOrderForCol[randomAttr.name] = originalRowIndex
                    shuffled += 1
                    pickedAttr.add(randomAttr)
                    # print("Shuffled", randomAttr)
                    break
                else:  # reset changes changes
                    refuteInstance = customDeepCopy(prevRefuteInstance)
                attempt += 1
        # print("Shuffled Cols:", shuffled, "Cols to Shuffle:", colToShuffle)
        if shuffled == colToShuffle:
            return refuteInstance, originalOrderForCol
        else:
            return None, None

    # @timed
    def removeTuple(self, table, rowsToRemove):
        if rowsToRemove > len(table.rows): return None
        # refuteInstance = customDeepCopy(table)
        refuteInstance = table
        for i in range(0, rowsToRemove):
            rowIndex = random.choice(range(0, len(table.rows)))
            refuteInstance.removeRow(rowIndex, init=False)
        refuteInstance.initPosForCells()
        return refuteInstance

    def addTuple(self, table, rowsToAdd, strategy, type, valuesForColumns):
        refuteInstance = customDeepCopy(table)
        for i in range(0, rowsToAdd):
            attempt = 0
            currentRowNumber = len(refuteInstance.rows)
            newRow = self.generateRow(table, strategy, currentRowNumber, type, valuesForColumns)
            while (self.rowPresent(table, newRow) and attempt < self.attemptsForRowGeneration):
                newRow = self.generateRow(table, strategy, currentRowNumber, type)
                attempt += 1
            if attempt < self.attemptsForRowGeneration: refuteInstance.addRow(newRow)
        refuteInstance.initPosForCells()
        return refuteInstance

    # @timed
    def addTupleBigTable(self, table, rowsToAdd, strategy, type, valuesForColumns):
        # refuteInstance = customDeepCopy(table)
        refuteInstance = table
        for i in range(0, rowsToAdd):
            currentRowNumber = len(refuteInstance.rows)
            newRow = self.generateRow(table, strategy, currentRowNumber, type, values=valuesForColumns)
            refuteInstance.addRow(newRow)
        refuteInstance.initPosForCells()
        return refuteInstance

    # @timed
    def updateValuesInColumn(self, refuteInstance, randomAttr, cellsForAttr):
        # shuffledInstance = customDeepCopy(refuteInstance)
        shuffledInstance = refuteInstance
        for i in range(0, len(cellsForAttr)):
            cell = cellsForAttr[i]
            cell.setRow(i)
            shuffledInstance.setCell(i, randomAttr, cell)
        return shuffledInstance

    def getRowIndexFromCells(self, cellsForAttr):
        rowIds = []
        for cell in cellsForAttr:
            rowIds.append(cell.getRowPos())
        return rowIds

    def countDifferences(self, cellsForAttr, cellsForAttrShuffled):
        counter = 0
        for c1, c2 in zip(cellsForAttr, cellsForAttrShuffled):
            if c1.value != c2.value: counter += 1
        return counter

    # @timed
    def generateRow(self, table, strategy, currentRowNumber, type, values=None):
        if strategy == Constants.STRATEGY_ACTIVE_DOMAIN:
            return self.newRowFromActiveDomain(table, currentRowNumber, type, values)
        if strategy == Constants.STRATEGY_LM_GENERATOR:
            return self.newRowFromLanguageModel(table, currentRowNumber, type)
        ## More Strategies HERE ##

    def newRowFromActiveDomain(self, table, currentRowNumber, type, valuesForColumn=None):
        newRow = []
        counterHeader = 0
        for header in table.schema:
            value = self.generateValueFromDomain(table, header, type, valuesForColumn)
            newCell = Cell(value, header)
            newCell.setPos([currentRowNumber, counterHeader])
            newRow.append(newCell)
            counterHeader += 1
        return newRow

    def newRowFromLanguageModel(self, table, currentRowNumber, type, valuesForColumn=None):
        newRow = []
        counterHeader = 0
        for header in table.schema:
            value = None
            if header.type == Constants.NUMERICAL:
                value = self.generateValueFromDomain(table, header, type, valuesForColumn)
            else:
                value = self.generateValueFromLanguageModel(table, header)
            newCell = Cell(value, header)
            newCell.setPos([currentRowNumber, counterHeader])
            newRow.append(newCell)
            counterHeader += 1
        return newRow

    def generateValueFromDomain(self, table, header, type, values=None):
        valuesInColumn = None
        if values is not None:
            valuesInColumn = values[header.name]
        else:
            valuesInColumn = table.getValuesForColumn(header.name)
        if header.type == Constants.NUMERICAL:
            minVal = min(valuesInColumn)
            maxVal = max(valuesInColumn)
            if type != Constants.STRATEGY_CHANGE_MIN and type != Constants.STRATEGY_CHANGE_MAX:
                if int(minVal) == minVal and int(maxVal) == maxVal:
                    value = int(random.randrange(minVal, maxVal))
                    return value
                else:
                    maxDigits = self.findMaxDigits(valuesInColumn)
                    value = round(random.uniform(minVal, maxVal), maxDigits)
                    return value
            else:
                minValRange = minVal - self.outOfRange
                maxValRange = maxVal + self.outOfRange
                valueMin = None
                valueMax = None
                if int(minVal) == minVal and int(maxVal) == maxVal:
                    valueMin = int(random.randrange(minValRange, minVal))
                    valueMax = int(random.randrange(maxVal, maxValRange))
                else:
                    maxDigits = self.findMaxDigits(valuesInColumn)
                    valueMin = round(random.uniform(minValRange, minVal), maxDigits)
                    valueMax = round(random.uniform(maxVal, maxValRange), maxDigits)
                if type == Constants.STRATEGY_CHANGE_MIN:
                    return valueMin
                elif type == Constants.STRATEGY_CHANGE_MAX:
                    return valueMax
                else:
                    return random.choice([valueMin, valueMax])
        else:
            value = random.choice(valuesInColumn)
            return value

    def rowPresent(self, table, newRow):
        rowList = table.rowsToString()
        newRowString = table.rowToString(newRow)
        return newRowString in rowList

    def findMaxDigits(self, valuesInColumn):
        maxDigits = 0
        for value in valuesInColumn:
            strVal = str(value).split(".")[1]
            lenDigits = len(strVal)
            if lenDigits > maxDigits: maxDigits = lenDigits
        return maxDigits

    def generateValueFromLanguageModel(self, table, header):
        valuesInColumn = table.getValuesForColumn(header.name)
        valuesForLM = None
        if len(valuesInColumn) > self.maxExamplesForLM:
            valuesForLM = random.sample(valuesInColumn, self.maxExamplesForLM)
        else:
            valuesForLM = valuesInColumn
        maxDistance = 0
        value = None
        for word in valuesForLM:
            newWord = self.lm.predictCellValue(word)
            distance = editdistance.eval(str(word), str(newWord))
            if distance > maxDistance:
                value = newWord
                maxDistance = distance
        return value

    # @timed
    def removeSameRowsBigTable(self, table, instance):
        # refuteInstance = customDeepCopy(instance)
        refuteInstance = instance
        refuteRows = refuteInstance.rowsToStringSet()
        originalRows = table.rowsToStringSet()
        rrToRemove = set()
        for rr in refuteRows:
            if rr in originalRows: rrToRemove.add(rr)
        refuteInstance.buildOptForRemove()
        for refuteRow in refuteInstance.rows[:]:
            stringRefuteRow = refuteInstance.rowToString(refuteRow)
            if stringRefuteRow in rrToRemove:
                refuteInstance.removeRowObj(refuteRow, False)
        refuteInstance.initPosForCells()
        return refuteInstance

    def removeSameRows(self, table, instance):
        refuteInstance = customDeepCopy(instance)
        refuteRows = refuteInstance.rowsToString()
        originalRows = table.rowsToString()
        rrToRemove = []
        for rr in refuteRows:
            if rr in originalRows: rrToRemove.append(rr)
        for refuteRow in refuteInstance.rows[:]:
            stringRefuteRow = refuteInstance.rowToString(refuteRow)
            if stringRefuteRow in rrToRemove:
                refuteInstance.removeRowObj(refuteRow, False)
        refuteInstance.initPosForCells()
        return refuteInstance

    def emptyCol(self, cellsInCol):
        for cell in cellsInCol:
            if cell.value is not None and len(str(cell.value).strip()) > 0:
                return False
        return True
