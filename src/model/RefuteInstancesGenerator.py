import random
import copy
import editdistance

from src import Constants
from src.model.RelationalTable import Cell
from src.textGeneration.FlanT5LM import FlanT5LM
import time


class RefuteInstancesGenerator:

    def __init__(self):
        self.seed = None
        self.attemptsForCol = 10
        self.attemptsForRowGeneration = 10
        self.outOfRange = 2
        self.maxExamplesForLM = 5 ## bigger is the number bigger is the time of the generation of one single cell
        self.lm = None

    def setSeed(self, seed):
        self.seed = seed
        random.seed(seed)

    def useLM(self):
        start_time = time.time()
        self.lm = FlanT5LM()
        end_time = time.time()
        #print("Loaded in (s): ", (end_time-start_time))

    def generateInstanceForRefute(self, table, addRows, rowsToAdd, removeRows, rowsToRemove, strategy):
        refuteInstance = copy.deepcopy(table)
        if rowsToAdd < 2 or removeRows:
            print("Warning. This configuration will not broke max or min values")
        if addRows and removeRows:
            print("Error. Cannot generate an instances with add and remove rows together")
            return None
        if rowsToAdd:
            if rowsToAdd == 1:
                refuteInstance = self.addTuple(refuteInstance, 1, strategy, Constants.STATEGY_CHANGE_MIN)
            elif rowsToAdd > 1:
                refuteInstance = self.addTuple(refuteInstance, 1, strategy, Constants.STATEGY_CHANGE_MIN)
                refuteInstance = self.addTuple(refuteInstance, 1, strategy, Constants.STATEGY_CHANGE_MAX)
                refuteInstance = self.addTuple(refuteInstance, rowsToAdd-2, strategy, "")
        elif rowsToRemove:
            refuteInstance = self.removeTuple(refuteInstance, rowsToRemove)
        if refuteInstance is not None:
            refuteInstance, _ = self.shuffleInstance(refuteInstance)
        refuteInstance = self.removeSameRows(table, refuteInstance) ## check if there are identical rows in both instances
        return refuteInstance

    def shuffleInstance(self, table):
        refuteInstance = copy.deepcopy(table)
        shuffled = 0
        colToShuffle = int (len(refuteInstance.schema) / 2)
        originalOrderForCol = {}
        pickedAttr = set()
        rowNumber = len(refuteInstance.rows)
        for i in range(0, colToShuffle):
            randomAttr = random.choice(refuteInstance.schema)
            attempt = 0
            while randomAttr in pickedAttr and attempt < self.attemptsForCol:
                randomAttr = random.choice(refuteInstance.schema)
                attempt+=1
            if attempt == self.attemptsForCol: break
            attempt = 0
            prevRefuteInstance = copy.deepcopy(refuteInstance)
            while attempt < self.attemptsForCol:
                cellsForAttr = refuteInstance.getCellsByHeader(randomAttr)
                originalCellsForAttr = refuteInstance.getCellsByHeader(randomAttr)
                random.shuffle(cellsForAttr)
                originalRowIndex = self.getRowIndexFromCells(cellsForAttr)
                self.updateValuesInColumn(refuteInstance, randomAttr, cellsForAttr)
                cellsForAttrShuffled = refuteInstance.getCellsByHeader(randomAttr)
                #print("*** ", self.countDifferences(originalCellsForAttr, cellsForAttrShuffled)," vs", rowNumber/2)
                if self.countDifferences(originalCellsForAttr, cellsForAttrShuffled) >= rowNumber/2:  #the half of the values are shuffled
                    originalOrderForCol[randomAttr.name] = originalRowIndex
                    shuffled += 1
                    pickedAttr.add(randomAttr)
                    break
                else:  # reset changes changes
                    refuteInstance = copy.deepcopy(prevRefuteInstance)
                attempt+=1
        if shuffled == colToShuffle:
            return refuteInstance, originalOrderForCol
        else:
            return None, None

    def removeTuple(self, table, rowsToRemove):
        if rowsToRemove > len(table.rows): return None
        refuteInstance = copy.deepcopy(table)
        for i in range(0, rowsToRemove):
            rowIndex = random.choice(range(0, len(table.rows)))
            refuteInstance.removeRow(rowIndex, init=False)
        refuteInstance.initPosForCells()
        return refuteInstance

    def addTuple(self, table, rowsToAdd, strategy, type):
        refuteInstance = copy.deepcopy(table)
        for i in range(0, rowsToAdd):
            attempt = 0
            currentRowNumber = len(refuteInstance.rows)
            newRow = self.generateRow(table, strategy, currentRowNumber, type)
            while(self.rowPresent(table, newRow) and attempt < self.attemptsForRowGeneration):
                newRow = self.generateRow(table, strategy, currentRowNumber, type)
                attempt += 1
            if attempt < self.attemptsForRowGeneration: refuteInstance.addRow(newRow)
        refuteInstance.initPosForCells()
        return refuteInstance

    def updateValuesInColumn(self, refuteInstance, randomAttr, cellsForAttr):
        for i in range(0, len(cellsForAttr)):
            cell = cellsForAttr[i]
            cell.setRow(i)
            refuteInstance.setCell(i, randomAttr, cell)

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

    def generateRow(self, table, strategy, currentRowNumber, type):
        if strategy == Constants.STRATEGY_ACTIVE_DOMAIN:
            return self.newRowFromActiveDomain(table, currentRowNumber, type)
        if strategy == Constants.STRATEGY_LM_GENERATOR:
            return self.newRowFromLanguageModel(table, currentRowNumber, type)
        ## More Strategies HERE ##

    def newRowFromActiveDomain(self, table, currentRowNumber, type):
        newRow = []
        counterHeader = 0
        for header in table.schema:
            value = self.generateValueFromDomain(table, header, type)
            newCell = Cell(value, header)
            newCell.setPos([currentRowNumber, counterHeader])
            newRow.append(newCell)
            counterHeader += 1
        return newRow

    def newRowFromLanguageModel(self, table, currentRowNumber, type):
        newRow = []
        counterHeader = 0
        for header in table.schema:
            value = None
            if header.type == Constants.NUMERICAL:
                value = self.generateValueFromDomain(table, header, type)
            else:
                value = self.generateValueFromLanguageModel(table, header)
            newCell = Cell(value, header)
            newCell.setPos([currentRowNumber, counterHeader])
            newRow.append(newCell)
            counterHeader += 1
        return newRow

    def generateValueFromDomain(self, table, header, type):
        valuesInColumn = table.getValuesForColumn(header.name)
        if header.type == Constants.NUMERICAL:
            minVal = min(valuesInColumn)
            maxVal = max(valuesInColumn)
            if type != Constants.STATEGY_CHANGE_MIN and type != Constants.STATEGY_CHANGE_MAX:
                if isinstance(minVal, int) and isinstance(maxVal, int):
                    value = random.randrange(minVal, maxVal)
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
                if isinstance(minVal, int) and isinstance(maxVal, int):
                    valueMin = random.randrange(minValRange, minVal)
                    valueMax = random.randrange(maxVal, maxValRange)
                else:
                    maxDigits = self.findMaxDigits(valuesInColumn)
                    valueMin = round(random.uniform(minValRange, minVal), maxDigits)
                    valueMax = round(random.uniform(maxVal, maxValRange), maxDigits)
                if type == Constants.STATEGY_CHANGE_MIN:
                    return valueMin
                elif type == Constants.STATEGY_CHANGE_MAX:
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
        if len (valuesInColumn) > self.maxExamplesForLM:
            valuesForLM = random.sample(valuesInColumn, self.maxExamplesForLM)
        else:
            valuesForLM = valuesInColumn
        maxDistance = 0
        value = None
        for word in valuesForLM:
            newWord = self.lm.predictCellValue(word)
            distance = editdistance.eval(word, newWord)
            if distance > maxDistance:
                value = newWord
                maxDistance = distance
        return value

    def removeSameRows(self, table, refuteInstance):
        refuteRows = refuteInstance.rowsToString()
        originalRows = table.rowsToString()
        rrToRemove = []
        for rr in refuteRows:
            if rr in originalRows: rrToRemove.append(rr)
        index = 0
        for refuteRow in refuteInstance.rows[:]:
            stringRefuteRow = refuteInstance.rowToString(refuteRow)
            if stringRefuteRow in rrToRemove:
                refuteInstance.removeRow(index, False)
            index += 1
        refuteInstance.initPosForCells()
        return refuteInstance



