import pandas as pd
from pandas.core.dtypes.common import is_numeric_dtype
from src import Constants

## UTILS METHODS
from src.LoggedDecorators import timed


def convertValue(value):
    if isinstance(value, int):
        try:
            integerValue = int(value)
            return integerValue
        except:
            pass
    try:
        floatValue = float(value)
        return floatValue
    except:
        pass
    try:
        valueWithoutComma = value.replace(",", ".")
        floatValue = float(valueWithoutComma)
        return floatValue
    except:
        pass
    return value

class Header:
    def __init__(self, name):
        self.name = name
        self.type = None

    def setType(self, type):
        self.type = type

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        if self.type is None:
            return self.name
        else:
            return self.name + "(" + self.type + ")"

    def __repr__(self):
        if self.type is None:
            return self.name
        else:
            return self.name + "("+self.type+")"

class Cell:
    def __init__(self, value, header, pos=[]):
        self.header = header
        self.value = value
        self.pos = pos

    def setRow(self, row):
        self.pos[0] = row

    def setPos(self, pos):
        self.pos = pos

    def getRowPos(self):
        return self.pos[0]

    def getColumnPos(self):
        return self.pos[1]

    def __repr__(self):
        return str(self.value)

    def toLongString(self):
        return "[" + str(self.pos[0]) + "][" + str(self.pos[1]) +"] - " + str(self.header) + ": " + str(self.value)

    def __hash__(self):
        return hash((self.header.name, self.value, self.pos[0], self.pos[1]))

    def __eq__(self, other):
        return (self.header.name, self.value, self.pos[0], self.pos[1]) == (other.name, other.value, other.pos[0], other.pos[1])

class Evidence:
    def __init__(self, tableName):
        self.rows = []
        self.orderedRows = []
        self.headers = []
        self.tableName = tableName
        self.key = None
        self.headerPos = dict()


    def setKey(self, attributeName):
        self.key = attributeName

    def getKey(self):
        if self.key == None: return self.headers[0].name
        return self.key

    def addRow(self, row):
        self.rows.append(row)

    def _findCellByHeader(self, header, row):
        for cell in row:
            if cell.header == header:
                return cell
        return None

    def getHeaderByName(self, headerName):
        if len(self.headerPos) > 0:
           if headerName in self.headerPos:
               pos = self.headerPos[headerName]
               return self.headers[pos]
        else:
            for header in self.headers:
                if header.name == headerName: return header
        return None

    def rowNumber(self):
        return len(self.rows)

    def singleColumnComplete(self):
        for header in self.headers:
            valuesForAttr = self.getValuesForAttr(header.name)
            if len(valuesForAttr) == len(self.rows): return True
        return False

    def getHeaderNames(self):
        headerNames = []
        for header in self.headers:
            headerNames.append(header.name)
        return headerNames

    def build(self):
        for row in self.rows:
            for cell in row:
                if cell.header not in self.headers:
                    self.headers.append(cell.header)
        for i in range(0, len(self.headers)):
            header = self.headers[i]
            self.headerPos[header.name] = i
        for row in self.rows:
            orderedRow = {}
            for header in self.headers:
                cell = self._findCellByHeader(header, row)
                if cell is not None:
                    cell.value = convertValue(cell.value)
                orderedRow[header.name] = cell
            self.orderedRows.append(orderedRow)

    def inferTypesFromDB(self, database):
        for header in self.headers:
            table = database.getTable(self.tableName, header.name)
            if table is None: ## without table default CATEGORICAL
                header.type = Constants.CATEGORICAL
                continue
            headerInTable = table.getAttribute(header.name)
            if headerInTable is not None:
                header.type = headerInTable.type

    def getValuesForAttr(self, attrName):
        values = []
        for orderedRow in self.orderedRows:
            cell = orderedRow[attrName]
            if cell is not None: ## skip none value
                values.append(cell.value)
        return values

    def isCompleteForAttribute(self, headerName):
        valuesForAttr = self.getValuesForAttr(headerName)
        return len(valuesForAttr) == len(self.rows)

    def isComplete(self):
        for header in self.headers:
            valuesForAttr = self.getValuesForAttr(header.name)
            if len(valuesForAttr) < len(self.rows): return False
        return True

    def __repr__(self):
        toReturn = ""
        for header in self.headers:
            toReturn += header.name+"|"
        toReturn += "\n"
        for row in self.rows:
            for header in self.headers:
                cell = self._findCellByHeader(header, row)
                cellValue = ""
                if cell is not None:
                    cellValue = cell.value
                toReturn += str(cellValue) + "|"
            toReturn += "\n"
        return toReturn

    def toListHeaders(self):
        headerList = []
        for header in self.headers:
            headerList.append(str(header.name))
        return headerList

    def toListCells(self):
        cellList = []
        for row in self.rows:
            for cell in row:
                if cell is not None: cellList.append(str(cell.value))
        return cellList


    def toList(self):
        tableList = []
        headerList = self.toListHeaders()
        tableList.append(headerList)
        for row in self.rows:
            rowList = []
            for cell in row:
                rowList.append(str(cell.value))
            tableList.append(rowList)
        return tableList

    def removeEmpty(self, values):
        cleaned = []
        for value in values:
            if len(str(value).strip()) > 0: cleaned.append(str(value).strip())
        return cleaned

    def toColumnsValues(self, splitTokens=True):
        dictReturn = {}
        listReturn = []
        for header in self.headers:
            values = self.getValuesForAttr(header.name)
            if len(values) == 0: continue
            cleaned = self.removeEmpty(values)
            if len(cleaned) == 0: continue
            headerName = header.name
            if len(headerName.strip()) == 0: headerName = "empty"
            dictReturn[header.name] = cleaned
            row = [headerName.split()]
            valuesList = []
            for value in cleaned:
                valuesList += str(value).strip().split()
            row.append(valuesList)
            listReturn.append(row)
        if splitTokens: return listReturn
        return dictReturn

    def getCellsForAttribute(self, attrName):
        cells = []
        for orderedRow in self.orderedRows:
            cell = orderedRow[attrName]
            if cell is not None:  ## skip none value
                cells.append(cell)
        return cells

    def getCellByRowAndAttr(self, row, attrName):
        return self.orderedRows[row][attrName]

    def getNumberOfCells(self):
        counter = 0
        for row in self.rows:
            for cell in row:
                if cell is not None and len(str(cell.value).strip())>0:
                    counter += 1
        return counter

class Table:
    def __init__(self, tableName, schema):
        self.tableName = tableName
        self.schema = schema
        self.rows = []
        self.orderedRows = []
        self.headerPos = dict()
        for i in range(0, len(self.schema)):
            header = self.schema[i]
            self.headerPos[header.name] = i
        ### for optimization
        self.lastRowsToDict = -1
        self.mapToDict = None
        self.rowStrings = None


    def addRow(self, row):
        self.rows.append(row)
        orderedRow = {}
        for header in self.schema:
            cell = self._findCellByHeader(header, row)
            orderedRow[header.name] = cell
        self.orderedRows.append(orderedRow)

    #@timed
    def toDict(self):
        if self.lastRowsToDict != len(self.rows):
            map = {}
            for header in self.schema:
                map[header.name] = []
            for row in self.orderedRows:
                for key, cell in row.items():
                    listOfValues = map[key]
                    value = convertValue(cell.value)
                    cell.value = value
                    listOfValues.append(value)
            self.lastRowsToDict = len(self.rows)
            self.mapToDict = map
            return map
        else:
            return self.mapToDict

    def toDictWithRowNumber(self):
        map = {}
        map['key'] = []
        for i in range(0, len(self.orderedRows)):
            map['key'] = i
        for header in self.schema:
            map[header.name] = []
        for row in self.orderedRows:
            for key, cell in row.items():
                listOfValues = map[key]
                value = convertValue(cell.value)
                cell.value = value
                listOfValues.append(value)
        return map

    def setType(self, attrName, type):
        for attribute in self.schema:
            if attribute.name == attrName:
                attribute.setType(type)

    def getAttribute(self, attrName):
        if len(self.headerPos) > 0:
            if attrName in self.headerPos:
                pos = self.headerPos[attrName]
                return self.schema[pos]
        else:
            for attribute in self.schema:
                if attribute.name == attrName:
                    return attribute
        return None

    def initPosForCells(self):
        rowIndex = 0
        for row in self.orderedRows:
            colIndex = 0
            for attr in self.schema:
                cell = row[attr.name]
                cell.setPos([rowIndex, colIndex])
                colIndex += 1
            rowIndex += 1

    def getCellByPos(self, row, col):
        attrName = self.schema[col].name
        return self.orderedRows[row][attrName]

    def getPosAttr(self, attrName):
        if len(self.headerPos) > 0:
            if attrName in self.headerPos:
                return self.headerPos[attrName]
        else:
            posReturn = 0
            for attribute in self.schema:
                if attribute.name == attrName: return posReturn
                posReturn += 1
        return -1

    def getCellsByHeader(self, header):
        cells = []
        for row in self.orderedRows:
            cell = row[header.name]
            cells.append(cell)
        return cells

    def setCell(self, rowNumber, header, cell):
        rowModify = self.rows[rowNumber]
        posMod = -1
        for i in range(0, len(rowModify)):
            cellOld = rowModify[i]
            if cellOld.header.name == cell.header.name:
                posMod = i
                break
        if posMod != -1: rowModify[posMod] = cell
        orderedRowModify = self.orderedRows[rowNumber]
        orderedRowModify[header.name] = cell

    def _findCellByHeader(self, header, row):
        if len(self.headerPos) > 0:
            if header.name in self.headerPos:
                pos = self.headerPos[header.name]
                return row[pos]
        else:
            for cell in row:
                if cell.header == header:
                    return cell
        return None

    def getValueForAggregate(self, column, operation):
        data = self.toDict()
        df = pd.DataFrame.from_dict(data)
        if operation == Constants.OPERATION_MIN:
            return min(df[column])
        if operation == Constants.OPERATION_MAX:
            return max(df[column])
        if operation == Constants.OPERATION_COUNT:
            return len(df[column])
        return None

    def getValuesForColumn(self, column):
        data = self.toDict()
        df = pd.DataFrame.from_dict(data)
        return df[column].tolist()

    def hasSameAttributes(self):
        setNames = set()
        for header in self.schema:
            setNames.add(header.name)
        if len(setNames) != len(self.schema): return True
        return False

    def removeRow(self, rowIndex, init=True):
        del self.rows[rowIndex]
        del self.orderedRows[rowIndex]
        if self.rowStrings is not None and len(self.rowStrings) > 0: del self.rowStrings[rowIndex]
        if init: self.initPosForCells()

    #@timed
    def buildOptForRemove(self):
        self.rowStrings = []
        for row in self.rows:
            self.rowStrings.append(self.rowToString(row))

    #@timed
    def removeRowObj(self, rowToDelete, init=True):
        index = -1
        rowStringDelete = self.rowToString(rowToDelete)
        if self.rowStrings is not None and len(self.rowStrings) > 0:
            for i in range(0, len(self.rowStrings)):
                if rowStringDelete == self.rowStrings[i]:
                    index = i
                    break
        else:
            for i in range(0, len(self.rows)):
                row = self.rows[i]
                if rowStringDelete == self.rowToString(row):
                    index = i
                    break
        if index != -1:
            self.removeRow(index, init)

    #@timed
    def rowsToStringSet(self):
        rowsString = set()
        for row in self.rows:
            toReturn = self.rowToString(row)
            rowsString.add(toReturn)
        return rowsString

    def rowsToString(self):
        rowsString = []
        for row in self.rows:
            toReturn = self.rowToString(row)
            rowsString.append(toReturn)
        return rowsString

    #@timed
    def rowToString(self, row):
        toReturn = ""
        for header in self.schema:
            cell = self._findCellByHeader(header, row)
            cellValue = ""
            if cell is not None:
                cellValue = cell.value
            toReturn += str(cellValue) + "|"
        return toReturn

    def __repr__(self):
        toReturn = "TABLE: " + self.tableName+"\n"
        for header in self.schema:
            toReturn += str(header) + "|"
            #toReturn += header.name+"|"
        toReturn += "\n"
        for row in self.rows:
            for header in self.schema:
                cell = self._findCellByHeader(header, row)
                cellValue = ""
                if cell is not None:
                    cellValue = cell.value
                toReturn += str(cellValue) + "|"
            toReturn += "\n"
        return toReturn

class Database:
    def __init__(self, name):
        self.name = name
        self.tables = []
        self.multipleHeaders = False

    def addTable(self, table):
        self.tables.append(table)

    def getTableByName(self, tableName):
        for table in self.tables:
            if table.tableName == tableName: return table
        return None

    #def getTable(self, tableName):
    #    for table in self.tables:
    #        if table.tableName == tableName: return table
    #    return None

    def getTable(self, tableName, attributeName):
        for table in self.tables:
            if (table.tableName == tableName) and (table.getAttribute(attributeName) is not None): return table
        return None

    def __repr__(self):
        toReturnDB = "DATABASE\n"
        for table in self.tables:
            toReturnDB += table.__repr__()
            toReturnDB += "\n\n"
        return toReturnDB

    def containsNonEmptyTables(self):
        for table in self.tables:
            if len(table.rows) > 0:
                return True
        return False

    def inferTypes(self):
        for table in self.tables:
            data = table.toDict()
            df = pd.DataFrame.from_dict(data)
            cols = df.columns
            dtypes = df.infer_objects().dtypes
            for attrName, attrType in dtypes.items():
                type = Constants.CATEGORICAL
                if is_numeric_dtype(attrType):
                    type = Constants.NUMERICAL
                table.setType(attrName, type)