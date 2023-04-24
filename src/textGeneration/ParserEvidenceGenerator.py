from src.model.RelationalTable import Header, Cell, Evidence, Table, Database
import re
import unicodedata

def cleanCellValue(string):
    #return re.sub(r"\[\[[^\|]*\|", "", str(string)).replace(']]', '').replace('[[', '')
    stringClean = unicodedata.normalize('NFKD', str(string)).encode('ascii', 'ignore').decode("ascii")
    regexPipe = r"\w*\|"
    return re.sub(regexPipe, "", str(stringClean), 0, re.MULTILINE).replace(("["),"").replace("]","").replace("\n", " ").strip()

def cleanAttributeName(string):
    attributeName = string.replace("[H]", "").strip()
    attributeName = cleanCellValue(attributeName)
    return attributeName

def isAttr(string):
    return "[H]" in string

def isHeader(row):
    countH = 0
    for cellText in row:
        if isAttr(cellText):
            countH += 1
    #return countH > (len(row)/2)
    return countH > 0

def dropEmptyTables(database):
    databaseNew = Database(database.name)
    for table in database.tables:
        #if len(table.rows) > 0 and (not table.hasSameAttributes()): databaseNew.addTable(table)
        if len(table.rows) > 0: databaseNew.addTable(table)
    return databaseNew

def checkEvidence(evidence, database):
    ## checks if the evidence is related to the table
    for attrName in evidence.getHeaderNames():
        table = database.getTable(evidence.tableName, attrName)
        if table is None: return False
        header = table.getAttribute(attrName)
        if header is None: return False
    return True

def parseRelationalTablesNotFeverous(tables, title):
    database = Database(title)
    currentTable = None
    for i in range(0, len(tables)):
        row = tables[i]
        if i == 0:
            headers = []
            for attrName in row:
                attributeName = cleanAttributeName(attrName)
                header = Header(attributeName)
                headers.append(header)
            currentTable = Table(title, headers)
        else:
            headers = currentTable.schema
            pos = 0
            rowForTable = []
            for cellValue in row:
                cellValue = cleanCellValue(cellValue)
                headerForCell = headers[pos]
                cell = Cell(cellValue, headerForCell)
                rowForTable.append(cell)
                pos += 1
            currentTable.addRow(rowForTable)
    if currentTable is not None:
        database.addTable(currentTable)
    return database

def parseRelationalTables(tables, title):
    database = Database(title)
    currentTable = None
    for row in tables:
        if isHeader(row):
            if currentTable is not None:
                database.addTable(currentTable)
            headers = []
            for attrName in row:
                if isAttr(attrName):
                    attributeName = cleanAttributeName(attrName)
                    header = Header(attributeName)
                    headers.append(header)
                    # if header not in headers:
                    #    headers.append(header)
            currentTable = Table(title, headers)
        else:
            if currentTable is not None:
                rowForTable = []
                headers = currentTable.schema
                pos = 0
                if len(row) != len(headers): continue
                for cellValue in row:
                    cellValue = cleanCellValue(cellValue)
                    headerForCell = headers[pos]
                    cell = Cell(cellValue, headerForCell)
                    rowForTable.append(cell)
                    pos += 1
                currentTable.addRow(rowForTable)
    if currentTable is not None:
        database.addTable(currentTable)
    # databaseCleaned = dropEmptyTables(database)
    databaseCleaned = database
    return databaseCleaned

def parseMultipleHeaders(tables, title):
    database = Database(title)
    database.multipleHeaders = True
    headersName = []
    headers = []
    table = None
    for row in tables:
        if isHeader(row):
            for i in range(0, len(row)):
                attrName = row[i]
                if isAttr(attrName):
                    attributeName = cleanAttributeName(attrName)
                    if len(headersName) < len(row):
                        headersName.append(attributeName)
                    else:
                        v = headersName[i]
                        newV = v + ", " + attributeName
                        headersName[i] = newV
        else:
            if len(headers) == 0:
                for attrName in headersName:
                    header = Header(attrName)
                    headers.append(header)
                    table = Table(title, headers)
            pos = 0
            rowForTable = []
            for cellValue in row:
                cellValue = cleanCellValue(cellValue)
                headerForCell = headers[pos]
                cell = Cell(cellValue, headerForCell)
                rowForTable.append(cell)
                pos += 1
            table.addRow(rowForTable)
    if table is not None:
        database.addTable(table)
    return database

def parseEntityTable(tables, title):
    transposed = list(map(list, zip(*tables)))
    database = parseRelationalTables(transposed, title)
    return database

def parseTables(tables, title, isFeverous=True):
    type, table = detect_type_table(tables)
    if type == "Relational_multipleheaderrows":
        return parseMultipleHeaders(tables, title)
    #if type == "EntityTable":
    #    return parseEntityTable(tables, title)
    ## best effort
    if isFeverous:
        return parseRelationalTables(tables, title)
    else:
        return parseRelationalTablesNotFeverous(tables, title)

def parseEvidence(evidenceFromFile, tableName, database, isFeverous, skipCheck=False):
    if isFeverous:
        evidence = Evidence(tableName)
        for row in evidenceFromFile:
            rowForEvidence = []
            for cell in row:
                cellValue = cell[0]
                attrValue = cell[1]
                if attrValue.count("[H]") > 1:
                    if (not skipCheck) and (not database.multipleHeaders):
                        tokens = attrValue.split(",")
                        attrValue = tokens[-1].strip()
                if attrValue == "": continue
                cellValue = cleanCellValue(cellValue)
                attrValue = cleanAttributeName(attrValue)
                cell = Cell(cellValue, Header(attrValue))
                rowForEvidence.append(cell)
            evidence.addRow(rowForEvidence)
        evidence.build()
        if skipCheck: return evidence
        evidence.inferTypesFromDB(database)
        if checkEvidence(evidence, database):
            return evidence
        else:
            return None
    else:
        evidence = Evidence(tableName)
        for row in evidenceFromFile:
            rowForEvidence = []
            for cell in row:
                cellValue = cell[0]
                attrValue = cell[1]
                cellValue = cleanCellValue(cellValue)
                attrValue = cleanAttributeName(attrValue)
                if attrValue == "": continue
                cell = Cell(cellValue, Header(attrValue))
                rowForEvidence.append(cell)
            evidence.addRow(rowForEvidence)
        evidence.build()
        if skipCheck: return evidence
        evidence.inferTypesFromDB(database)
        if checkEvidence(evidence, database):
            return evidence
        else:
            return None


def detect_type_table(table):
    header_rows = []
    identical_rows = []
    header_cols = []
    type_table = None
    for row_nb in range(len(table)):
        if len([x for x in table[row_nb] if '[H]' in x]) == len([x for x in table[row_nb]]):
            header_rows += [row_nb]
        if len(list(set([x for x in table[row_nb]]))) == 1:
            identical_rows += [row_nb]
    for col_nb in range(len(table[0])):
        if len([x[col_nb] for x in table if '[H]' in x[col_nb]]) == len([x[col_nb] for x in table]):
            header_cols += [col_nb]
    for row in enumerate(table):
        for col in enumerate(row[1]):
            if '[H]' in col[1]:
                if not (col[0] in header_cols) and not (row[0] in header_rows):
                    type_table = 'NotStructuredHeaders'
                    return [type_table, None]
    if len(header_rows) == 1 and len(header_cols) == 0:
        type_table = 'Relational'
        return [type_table, None]
    if len(header_rows) == 1 and len(header_cols) > 1 and not (set(header_rows) in set(identical_rows)):
        type_table = 'Relational_parasitecols'
        return [type_table, None]
    if len(header_rows) > 1 and len(header_cols) == 0:
        type_table = 'Relational_multipleheaderrows'
        return [type_table, None]
    if len(header_rows) > 1 and len(header_cols) > 1 and not (set(header_rows) in set(identical_rows)):
        type_table = 'Relational_multipleheaderrows_parasitecols'
        return [type_table, None]
    if (set(header_rows).issubset(identical_rows)) and len(header_cols) == 1:
        type_table = 'EntityTable'

        ####Now we start the conversion

        # each elt is a dict representing a col, and each dict of col contains the various rows.
        new_table_dict_cols = dict()

        ##each elt of index_switch: [[oldrow,oldcol],[newrow,newcol]]
        index_switch = []

        ##list of headers like this: colvalue
        used_cols = []

        current_index = 0
        nb_cols = 0
        nb_rows = 0

        max_row_nb = 0
        for row_tot in enumerate(table):
            row_nb = row_tot[0]
            row_val = row_tot[1]
            if row_nb in header_rows:
                continue
            if row_val[header_cols[0]] in used_cols:
                ###Multiple cols with same value, unknown
                type_table = 'EntityTable_multiplecolssamevalue'
                return [type_table, None]
            used_cols += [row_val[header_cols[0]]]
            new_table_dict_cols[current_index] = [row_val[header_cols[0]]]
            index_switch += [[[row_nb, header_cols[0]], [0, current_index]]]
            current_new_row = 1
            for col_tot in enumerate(row_val):
                col_nb = col_tot[0]
                col_val = col_tot[1]
                if col_nb in header_cols:
                    continue
                new_table_dict_cols[current_index] += [row_val[col_nb]]

                index_switch += [[[row_nb, col_nb], [current_new_row, current_index]]]
                current_new_row += 1
            max_row_nb = max(max_row_nb, current_new_row)
            current_index += 1
        new_table = []
        for row_nb in range(max_row_nb):
            row_value = []
            for col_nb in range(current_index):
                entire_col = new_table_dict_cols[col_nb]
                if len(entire_col) > row_nb:
                    row_value += [entire_col[row_nb]]

            new_table += [row_value]
        return [type_table, [new_table, index_switch]]
    else:
        type_table = 'Unknown'
        return [type_table, None]
