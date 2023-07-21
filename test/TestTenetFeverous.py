import unittest
import json
import unicodedata
import re
import time
import csv
import traceback
import ast

from src import Constants
from src.Statistics import Statistics
from src.Tenet import Tenet
from src.feverous.database.feverous_db import FeverousDB
from src.feverous.utils.wiki_page import WikiPage
from src.model.RefuteInstancesGenerator import RefuteInstancesGenerator
from src.model.RelationalTable import Table, Header, Cell, Database, Evidence

import logging

from src.textGeneration.FlanT5LM import FlanT5LM

logger = logging.getLogger(__name__)
logger.setLevel("ERROR")

####################
## UTILS Methods
####################
def loadDocIds():
    f = open('../data/pair_title_tablenb.json')
    data = json.load(f)
    f.close()
    docIds = set()
    for item in data:
        docIds.add(item[0] + "_" + str(item[1]))
    return docIds


def loadFeverousEvidences():
    f = open('../data/feverous_train_challenges.json')
    data = json.load(f)
    f.close()
    return data

def loadJsonL(fileName):
    #f = open('../data/revision/original_dev.jsonl')
    f = open(fileName)
    examples = []
    f.readline()
    for line in f:
        example = json.loads(line)
        examples.append(example)
    f.close()
    return examples

def loadAdults():
    rows = []
    attributes = []
    with open('../data/revision/adult.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        readHeader = True
        for row in reader:
            rowValue = []
            for cell in row:
                if readHeader:
                    attributes.append(cell)
                else:
                    rowValue.append(cell)
            readHeader = False
            if len(rowValue) > 0: rows.append(rowValue)
    headersTenet = []
    posHeaders = {}
    counter = 0
    for attrName in attributes:
        attr = Header(attrName)
        headersTenet.append(attr)
        posHeaders[counter] = attr
        counter += 1
    tableTenet = Table("adult", headersTenet)
    rowIndex = 0
    for row in rows:
        rowTenet = []
        for i in range(0, len(row)):
            cellValue = row[i]
            headerTenet = posHeaders[i]
            cell = Cell(cellValue, headerTenet, [rowIndex, i])
            rowTenet.append(cell)
        tableTenet.addRow(rowTenet)
    database = Database("Test")
    database.addTable(tableTenet)
    database.inferTypes()
    return database

def getCellsFromEvidence(evidence):
    selectedCells = evidence["content"]
    filteredCells = []
    pages = set()
    tables = set()
    for cell in selectedCells:
        if cell.split("_")[1] == "cell":
            filteredCells.append(cell[cell.index("_") + 1:])
            pages.add(cell.split("_")[0])
            tables.add(cell.split("_")[2])
    if (len(pages) != 1 or len(tables) != 1): return None, None, None
    return list(pages)[0], list(tables)[0], filteredCells

def getCellsFromEvidenceFeverous(selectedCells, pattern):
    wikiDataStructure = {}
    for cell in selectedCells:
        if cell.split("_")[1] == pattern:
            cellId = cell[cell.index("_") + 1:]
            page = cell.split("_")[0]
            table = cell.split("_")[2]
            if page not in wikiDataStructure:
                tableDict = {table: [cellId]}
                wikiDataStructure[page] = tableDict
            else:
                tableDict = wikiDataStructure[page]
                if table not in tableDict:
                    tableDict[table] = [cellId]
                else:
                    cellList = tableDict[table]
                    cellList.append(cellId)
    return wikiDataStructure

def getCellListFromEvidenceFeverous(evContent, db):
    dataStructure = getCellsFromEvidenceFeverous(evContent, "cell")
    #print(dataStructure)
    evidenceCellList = []
    for wikipage, tables in dataStructure.items():
        page_json = db.get_doc_json(wikipage)
        wiki_page = WikiPage(wikipage, page_json)
        for tableId, cells in tables.items():
            try:
                wiki_table = wiki_page.get_tables()[int(tableId)]
                for cell in cells:
                    evidenceCellList.append(cleanCellValue(wiki_table.get_cell_content(cell)))
            except:
                pass
    return evidenceCellList, dataStructure.keys()

def getHeadeListsFromEvidenceFeverous(evContext, db):
    contextHeadersList = []
    for cellId, values in evContext.items():
        dataStructure = getCellsFromEvidenceFeverous(values, "header")
       # print(dataStructure)
        for wikipage, cellDict in dataStructure.items():
            page_json = db.get_doc_json(wikipage)
            wiki_page = WikiPage(wikipage, page_json)
            for cell, headers in cellDict.items():
                for header in headers:
                    splits = header.split("_")
                    tableId = int(splits[2])
                    headerRowId = int(splits[-2])
                    headerColumnId = int(splits[-1])
                    #print(header, "TableID", tableId, "HeaderRowID", headerRowId, "ColumnID", headerColumnId)
                    wikiTable = wiki_page.get_tables()[tableId]
                    #print("Rows in wiki:", len(wikiTable.get_header_rows()))
                    headerValue = wiki_page.get_cell_content(header)
                    headerValue = headerValue.replace("[","").replace("]","")
                    contextHeadersList.append(headerValue)
                    #headerRow = wikiTable.get_header_rows()[headerRowId]
                    #headerWiki = headerRow.row[headerColumnId]
                    #contextHeadersList.append(str(headerWiki))
    return contextHeadersList

def getFeverousExamples(examples, db):
    feverousExamples = []
    for example in examples:
        claim = example['claim']
        evidencesList = example['evidence']
        tables = set()
        allEvidences = []
        allContext = []
        id = example['id']
        for ev in evidencesList:
            try:
                evCellList, wikiPages = getCellListFromEvidenceFeverous(ev["content"], db)
                if len(evCellList) == 0: continue
                tables.update(list(wikiPages))
                #print("** EV CELL LIST:", evCellList)
                allEvidences += evCellList
                contextHeadersList = getHeadeListsFromEvidenceFeverous(ev['context'], db)
                allContext += contextHeadersList
            except:
                print("Exception with:", claim, "ID:", id)
                dataStructure = getCellsFromEvidenceFeverous(ev["content"], "cell")
                #print(dataStructure)
                raise Exception(claim, "ID:", id)
        label = example['label']
        evidence = allEvidences
        context = allContext
        fevExample = {"claim": claim, "label": label, "evidence": evidence,
                      "evidence_ctxt": context, "title": tables, "id": id}
        feverousExamples.append(fevExample)
    return feverousExamples

def cleanCellValue(string):
    stringClean = unicodedata.normalize('NFKD', str(string)).encode('ascii', 'ignore').decode("ascii")
    cleaned_text = re.sub(r'\[\[.*?\|', '', stringClean)
    cleaned_text = re.sub(r'\]\]', '', cleaned_text)
    return cleaned_text

def cleanCellValueEnzo(string):
    #return re.sub(r"\[\[[^\|]*\|", "", str(string)).replace(']]', '').replace('[[', '')
    stringClean = unicodedata.normalize('NFKD', str(string)).encode('ascii', 'ignore').decode("ascii")
    regexPipe = r"\w*\|"
    return re.sub(regexPipe, "", str(stringClean), 0, re.MULTILINE).replace(("["),"").replace("]","").replace("\n", " ").strip()

def wikiTableToTable(wikiTable, tableName):
    headerRow = True
    headers = []
    rows = []
    rowIndex = 0
    for row in wikiTable.get_rows():
        rowTable = []
        counterColumn = 0
        for cell in row.row:
            if headerRow:
                header = Header(cleanCellValue(cell.content))
                headers.append(header)
            else:
                cellObj = Cell(cleanCellValue(cell.content), headers[counterColumn], [rowIndex, counterColumn])
                rowTable.append(cellObj)
            counterColumn += 1
        if not headerRow:
            rows.append(rowTable)
            rowIndex += 1
        headerRow=False
    table = Table(tableName, headers)
    for row in rows:
        table.addRow(row)
    database = Database(tableName)
    database.addTable(table)
    database.inferTypes()
    return database

def wikiCellsToEvidence(cells, database, wiki_page_name):
    rowDict = {}
    ###cell_0_1_2
    for cell in cells:
        row = int(cell.split("_")[-2])
        column = int(cell.split("_")[-1])
        if row not in rowDict:
            rowDict[row] = []
        columns = rowDict[row]
        columns.append(column)
    table = database.getTableByName(wiki_page_name)
    evidenceRows = []
    #print(rowDict)
    for row, cells in rowDict.items():
        evidenceRow = []
        for cell in cells:
            #print("Row-Cell", row, cell)
            cellForEvidence = table.getCellByPos(row-1, cell)
            evidenceRow.append(cellForEvidence)
        evidenceRows.append(evidenceRow)
    evidence = Evidence(wiki_page_name)
    for evidenceRow in evidenceRows:
        evidence.addRow(evidenceRow)
    evidence.build()
    return evidence

def duplicatedAttrs(schema):
    mapData = {}
    for attr in schema:
        if attr.name not in mapData:
            mapData[attr.name] = 0
        mapData[attr.name] += 1
    for attrName, counter in mapData.items():
        if counter > 1: return True
    return False
####################
class TestTenetFeverous(unittest.TestCase):

    def setUp(self):
        headerName = Header("Name")
        headerAge = Header("Age")
        headerLoc = Header("Loc")
        table1 = Table("Persons", [headerName, headerAge, headerLoc])
        table1.addRow([Cell("Mike", headerName), Cell(47, headerAge), Cell("SF", headerLoc)])
        table1.addRow([Cell("Anne", headerName), Cell(22, headerAge), Cell("NY", headerLoc)])
        table1.addRow([Cell("John", headerName), Cell(12, headerAge), Cell("NY", headerLoc)])
        table1.addRow([Cell("Paul", headerName), Cell(8, headerAge), Cell("NY", headerLoc)])
        headerScore = Header("Score")
        headerExam = Header("Exam")
        table2 = Table("University Career", [headerName, headerScore, headerExam])
        table2.addRow([Cell("Mike", headerName), Cell(10, headerScore), Cell("PP", headerExam)])
        table2.addRow([Cell("Mike", headerName), Cell(9, headerScore), Cell("POOI", headerExam)])
        table2.addRow([Cell("John", headerName), Cell(8, headerScore), Cell("A1", headerExam)])
        table2.addRow([Cell("Paul", headerName), Cell(4, headerScore), Cell("NET1", headerExam)])
        self.database = Database("Test")
        self.database.addTable(table1)
        self.database.addTable(table2)
        self.database.inferTypes()

        self.evidenceSingleRow = Evidence("Persons")
        cell0_0 = Cell("Mike", Header("Name"))
        cell0_0.setPos([0, 0])
        cell0_1 = Cell(47, Header("Age"))
        cell0_1.setPos([0, 1])
        self.evidenceSingleRow.addRow([cell0_0, cell0_1])
        self.evidenceSingleRow.build()

        self.evidenceMultipleRows = Evidence("Persons")
        cell0_2 = Cell("SF", Header("Loc"))
        cell0_2.setPos([0, 2])
        self.evidenceMultipleRows.addRow([cell0_0, cell0_2])
        cell1_0 = Cell("Anne", Header("Name"))
        cell1_0.setPos([1, 0])
        cell1_1 = Cell(22, Header("Age"))
        cell1_1.setPos([1, 1])
        cell1_2 = Cell("NY", Header("Loc"))
        cell1_2.setPos([1, 2])
        self.evidenceMultipleRows.addRow([cell1_0, cell1_2])
        self.evidenceMultipleRows.build()

        self.evidenceMultipleRowsNumerical = Evidence("Persons")
        cell0_2 = Cell("SF", Header("Loc"))
        cell0_2.setPos([0, 2])
        self.evidenceMultipleRowsNumerical.addRow([cell0_0, cell0_1])
        cell1_0 = Cell("Anne", Header("Name"))
        cell1_0.setPos([1, 0])
        cell1_1 = Cell(22, Header("Age"))
        cell1_1.setPos([1, 1])
        cell1_2 = Cell("NY", Header("Loc"))
        cell1_2.setPos([1, 2])
        self.evidenceMultipleRowsNumerical.addRow([cell1_0, cell1_1])
        self.evidenceMultipleRowsNumerical.build()

        self.evidenceFullColumn = Evidence("Persons")
        self.evidenceFullColumn.addRow([cell0_0, cell0_1])
        self.evidenceFullColumn.addRow([cell1_1])
        cell2_1 = Cell(12, Header("Age"))
        cell2_1.setPos([2, 1])
        self.evidenceFullColumn.addRow([cell2_1])
        cell3_1 = Cell(18, Header("Age"))
        cell3_1.setPos([3, 1])
        self.evidenceFullColumn.addRow([cell3_1])
        self.evidenceFullColumn.build()

    def tearDown(self):
        pass

    def test_generate_singleEvidenceAddRows(self):
        tableName = self.evidenceSingleRow.tableName
        evidenceSel = self.evidenceSingleRow
        numEvidence = 10 ## generated evidences, filtered with bestEvidences
        addRows = True
        rowsToAdd= 3
        removeRows = False
        rowsToRemove = 0
        useLM = False
        strategy = Constants.STRATEGY_ACTIVE_DOMAIN
        if strategy == Constants.STRATEGY_LM_GENERATOR:
            useLM = True
        seed = 17
        operations = [Constants.OPERATION_LOOKUP, Constants.OPERATION_COMPARISON, Constants.OPERATION_FILTER,
                      Constants.OPERATION_MIN, Constants.OPERATION_MAX, Constants.OPERATION_COUNT,
                      Constants.OPERATION_SUM, Constants.OPERATION_AVG]
        comparisons = [Constants.OPERATOR_SAME, Constants.OPERATOR_LT, Constants.OPERATOR_GT]
        languageModel = Constants.LANGUAGE_MODEL_CHAT_GTP
        bestEvidences = 5
        sentencesPerExample = 3
        rateLimit = True
        sleepTime = 21  ## rateLimit 3 requests per minute
        tenet = Tenet(self.database, seed, operations, comparisons, bestEvidences, sentencesPerExample, languageModel, rateLimit, sleepTime)
        positiveExamples = tenet.generatePositiveExamples(tableName, evidenceSel, numEvidence)
        negativeExamples = tenet.generateNegativeExamples(tableName, evidenceSel, numEvidence, addRows, rowsToAdd, removeRows, rowsToRemove, strategy, useLM=useLM)
        table = self.database.getTableByName(tableName)
        print(table)
        print("***** POSITIVES *****")
        for p in positiveExamples:
            print(p["evidence"])
            print(p["sentences"])
        print("***** NEGATIVES *****")
        for n in negativeExamples:
            print(n["evidence"])
            print(n["sentences"])

    def test_generate_evidenceMultipleRowsNumerical(self):
        tableName = self.evidenceMultipleRowsNumerical.tableName
        evidenceSel = self.evidenceMultipleRowsNumerical
        numEvidence = 10 ## generated evidences, filtered with bestEvidences
        addRows = True
        rowsToAdd= 3
        removeRows = False
        rowsToRemove = 0
        useLM = False
        strategy = Constants.STRATEGY_ACTIVE_DOMAIN
        if strategy == Constants.STRATEGY_LM_GENERATOR:
            useLM = True
        seed = 17
        operations = [Constants.OPERATION_LOOKUP, Constants.OPERATION_COMPARISON, Constants.OPERATION_FILTER,
                      Constants.OPERATION_MIN, Constants.OPERATION_MAX, Constants.OPERATION_COUNT,
                      Constants.OPERATION_SUM, Constants.OPERATION_AVG]
        comparisons = [Constants.OPERATOR_SAME, Constants.OPERATOR_LT, Constants.OPERATOR_GT]
        languageModel = Constants.LANGUAGE_MODEL_CHAT_GTP
        bestEvidences = 5
        sentencesPerExample = 3
        rateLimit = True
        sleepTime = 4  ## rateLimit 3 requests per minute
        tenet = Tenet(self.database, seed, operations, comparisons, bestEvidences, sentencesPerExample, languageModel, rateLimit, sleepTime)
        ## if evidenceSel is None then Cold
        positiveExamples = tenet.generatePositiveExamples(tableName, evidenceSel, numEvidence)
        negativeExamples = tenet.generateNegativeExamples(tableName, evidenceSel, numEvidence, addRows, rowsToAdd, removeRows, rowsToRemove, strategy, useLM=useLM)
        table = self.database.getTableByName(tableName)
        print(table)
        print("***** POSITIVES *****")
        for p in positiveExamples:
            print(p["evidence"])
            print(p["sentences"])
        print("***** NEGATIVES *****")
        for n in negativeExamples:
            print(n["evidence"])
            print(n["sentences"])

    def test_feverous_load(self):
        statistics = Statistics()
        feverousEvidences = loadFeverousEvidences()
        docIds = loadDocIds()
        db = FeverousDB("../data/filtereddb_st_2.db")
        #db = FeverousDB("../data/feverous_wikiv1.db")
        ###############
        printOutput = False
        numEvidence = 10  ## generated evidences, filtered with bestEvidences
        addRows = True
        rowsToAdd = 2
        removeRows = False
        rowsToRemove = 0
        useLM = False
        lmNegative = None
        coldStart = False
        if useLM: lmNegative = FlanT5LM()
        strategy = Constants.STRATEGY_ACTIVE_DOMAIN
        #strategy = Constants.STRATEGY_LM_GENERATOR
        if strategy == Constants.STRATEGY_LM_GENERATOR: useLM = True
        seed = 17
        operations = [Constants.OPERATION_LOOKUP, Constants.OPERATION_COMPARISON, Constants.OPERATION_FILTER,
                      Constants.OPERATION_MIN, Constants.OPERATION_MAX, Constants.OPERATION_COUNT,
                      Constants.OPERATION_SUM, Constants.OPERATION_AVG, Constants.OPERATION_RANKED, Constants.OPERATION_PERCENTAGE]
        comparisons = [Constants.OPERATOR_SAME, Constants.OPERATOR_LT, Constants.OPERATOR_GT]
        languageModel = Constants.LANGUAGE_MODEL_CHAT_GTP
        bestEvidences = 1
        sentencesPerExample = 3
        rateLimit = True
        sleepTime = 5  ## rateLimit 3 requests per minute
        feverousExampleToUse=25
        reverseOrderTables = False
        if reverseOrderTables: feverousEvidences.reverse()
        ###############
        counterExplored = 0
        counterPositive = 0
        counterNegative = 0
        positivesGenerated = []
        negativesGenerated = []
        for feverousEvidence in feverousEvidences:
            if ("evidence" not in feverousEvidence): continue
            if (len(feverousEvidence["evidence"]) != 1): continue
            wiki_page_name, wiki_table_id, cells = getCellsFromEvidence(feverousEvidence["evidence"][0])
            if (wiki_page_name == None or wiki_table_id == None or cells == None): continue
            if (wiki_page_name + "_" + str(wiki_table_id) not in docIds): continue
            #print("*** Wiki Page: ", wiki_page_name, wiki_table_id, cells)
            page_json = db.get_doc_json(wiki_page_name)
            wiki_page = WikiPage(wiki_page_name, page_json)
            wiki_table = wiki_page.get_tables()[int(wiki_table_id)]
            if wiki_page_name in ["Wilford Hundred", "Arturo Maffei", "Colorado State Highway 92","Erhard Loretan","Eurocup Basketball 2013–14 Last 32 Group L", "Shire of Isisford"]: continue ## due to tokens limit for chatGPT
            database = wikiTableToTable(wiki_table, wiki_page_name)
            table = database.getTableByName(wiki_page_name)
            if duplicatedAttrs(table.schema): continue
            #print(database)
            evidence = wikiCellsToEvidence(cells, database, wiki_page_name)
            if printOutput: print(database)
            if printOutput: print(evidence)
            if coldStart: evidence = None
            #### TENET GENERATION
            tenet = Tenet(database, seed, operations, comparisons, bestEvidences, sentencesPerExample, languageModel,
                          rateLimit, sleepTime)
            #tenet.disableLanguageModel()
            tenet.setStatistics(statistics)
            if lmNegative is not None: tenet.refutesInstancesGenerator.setLM(lmNegative)
            try:
                positiveExamples = tenet.generatePositiveExamples(wiki_page_name, evidence, numEvidence)
                counterPositive += len(positiveExamples)
                if printOutput: print("***** POSITIVES *****")
                for p in positiveExamples:
                    positivesGenerated.append(p)
                    if printOutput: print(p["evidence"])
                    if printOutput: print(p["sentences"])
                    if printOutput: print(p["s-operation"])
                    if printOutput: print("**"*10)
            except Exception as e:
                print(e)
                traceback.print_exc()
            try:
                negativeExamples = tenet.generateNegativeExamples(wiki_page_name, evidence, numEvidence, addRows, rowsToAdd, removeRows, rowsToRemove, strategy, useLM=useLM)
                counterNegative += len(negativeExamples)
                if printOutput: print("***** NEGATIVES *****")
                for n in negativeExamples:
                    negativesGenerated.append(n)
                    if printOutput: print(n["evidence"])
                    if printOutput: print(n["sentences"])
                    if printOutput: print(p["s-operation"])
                    if printOutput: print("**" * 10)
            except Exception as e:
                print(e)
                traceback.print_exc()
                #pass
            #break
            counterExplored += 1
            #print("Explored:", counterExplored)
            if counterExplored >= feverousExampleToUse: break
        statistics.print()
        print("Positive Generated: ", counterPositive)
        print("Negative Generated: ", counterNegative)
        totalCost = (statistics.data[Constants.STATISTICS_USED_TOKENS]/1000) * 0.002
        print("Costs ($):", totalCost)
        print("Tokens:", statistics.data[Constants.STATISTICS_USED_TOKENS])
        feverousOutput = []
        for p in positivesGenerated:
            sentences = p["sentences"]
            firstS = None
            for s in sentences:
                if s not in Constants.LANGUAGE_MODEL_CHAT_GTP_ERRORS:
                    firstS = s
                    break
            if firstS is not None:
                evidence = p["evidence"]
                evidence_ctxt = p["evidence"] ## ???
                title = p["table"].tableName
                label = "SUPPORTS"
                fevExample = {"claim": firstS, "label": label, "evidence": evidence.toListCells(),
                              "evidence_ctxt": evidence_ctxt.toListHeaders(), "title": title}
                feverousOutput.append(fevExample)
        for n in negativesGenerated:
            sentences = n["sentences"]
            firstS = None
            for s in sentences:
                if s not in Constants.LANGUAGE_MODEL_CHAT_GTP_ERRORS:
                    firstS = s
                    break
            if firstS is not None:
                evidence = n["evidence"]
                evidence_ctxt = n["evidence"]
                title = n["table"].tableName
                label = "REFUTES"
                if evidence is not None:
                    fevExample = {"claim": firstS, "label": label, "evidence": evidence.toListCells(), "evidence_ctxt": evidence_ctxt.toListHeaders(), "title": title}
                    feverousOutput.append(fevExample)
        type = "_warm_"
        if coldStart: type = "_cold_"
        if reverseOrderTables: type += "reversed_"
        fileName = "./tenet_generated"+ type + str(feverousExampleToUse)+".jsonl"
        print("Save to: ", fileName)
        with open(fileName, 'w') as f:
            for output in feverousOutput:
                stringSave = str(output)
                f.write(stringSave)
                f.write("\n")
        print("File exported.")


    def test_adults_load(self):
        statistics = Statistics()
        ### TENET CONFIG
        numEvidence = 2  ## generated evidences, filtered with bestEvidences
        addRows = True
        rowsToAdd = 3
        removeRows = False
        rowsToRemove = 0
        useLM = False
        strategy = Constants.STRATEGY_ACTIVE_DOMAIN
        if strategy == Constants.STRATEGY_LM_GENERATOR: useLM = True
        seed = 17
        operations = [Constants.OPERATION_LOOKUP, Constants.OPERATION_COMPARISON, Constants.OPERATION_FILTER,
                      Constants.OPERATION_MIN, Constants.OPERATION_MAX, Constants.OPERATION_COUNT,
                      Constants.OPERATION_SUM, Constants.OPERATION_AVG]
        #operations = [Constants.OPERATION_MIN, Constants.OPERATION_MAX]
        comparisons = [Constants.OPERATOR_SAME, Constants.OPERATOR_LT, Constants.OPERATOR_GT]
        languageModel = Constants.LANGUAGE_MODEL_CHAT_GTP
        bestEvidences = 1
        sentencesPerExample = 3
        rateLimit = True
        sleepTime = 5  ## rateLimit 3 requests per minute
        ###############
        ################

        database = loadAdults()

        table = database.getTableByName("adult")
        table.initPosForCells()
        #print(table.getCellByPos(0,0),table.getCellByPos(0,1), table.getCellByPos(0,3))
        evidenceSingleRow = Evidence("adult")
        evidenceSingleRow.addRow([table.getCellByPos(0,0),table.getCellByPos(0,1), table.getCellByPos(0,3)])
        evidenceSingleRow.build()

        evidenceMultipleRows = Evidence("adult")
        evidenceMultipleRows.addRow([table.getCellByPos(0, 0), table.getCellByPos(0, 1)])
        evidenceMultipleRows.addRow([table.getCellByPos(1, 0), table.getCellByPos(1, 1)])
        evidenceMultipleRows.build()

        evidenceFilterJapan = Evidence("adult")
        attrAgePos = 0
        attrNativeCountry = 13
        for rowIndex in range(0, len(table.rows)):
            rowTenet = table.rows[rowIndex]
            if str(rowTenet[attrNativeCountry].value).strip() == "Japan":
                evidenceFilterJapan.addRow([table.getCellByPos(rowIndex, attrAgePos), table.getCellByPos(rowIndex, attrNativeCountry)])
        evidenceFilterJapan.build()

        evidences = [evidenceSingleRow, evidenceMultipleRows, evidenceFilterJapan]
        #evidences = [evidenceSingleRow]

        ### for big tables, the refute instances is generated once
        refutesInstancesGenerator = RefuteInstancesGenerator()
        refutesInstancesGenerator.setSeed(seed)
        refuteInstances = refutesInstancesGenerator.generateInstanceForRefuteBigTables(table, addRows, rowsToAdd, removeRows, rowsToRemove, strategy, None, evidences=evidences)

        for evidence in evidences:
            #### TENET GENERATION
            try:
                tenet = Tenet(database, seed, operations, comparisons, bestEvidences, sentencesPerExample,
                              languageModel, rateLimit, sleepTime)
                tenet.disableLanguageModel()
                tenet.setStatistics(statistics)
                print("Generate Positives")
                positiveExamples = tenet.generatePositiveExamples("adult", evidence, numEvidence)
                print("Generate Negatives")
                negativeExamples = tenet.generateNegativeExamples("adult", evidence, numEvidence, addRows, rowsToAdd,
                                                                  removeRows, rowsToRemove, strategy, useLM=useLM,
                                                                  instanceRefute=refuteInstances)
            except Exception as e:
                print(e)

        statistics.print()

    def test_feverous_colab(self):
        db = FeverousDB("../data/feverous_wikiv1.db")
        examplesDev = loadJsonL('../data/revision/original_dev_corrected.jsonl')
        feverousDev = getFeverousExamples(examplesDev, db)
        examplesTrain = loadJsonL('../data/revision/feverous_train_challenges_only_tables_evidence_add_filtered_st_v2.jsonl')
        feverousTrain = getFeverousExamples(examplesTrain, db)
        print(len(examplesTrain), len(feverousTrain))
        fileName = "./feverous_train.jsonl"
        with open(fileName, 'w') as f:
            for output in feverousTrain:
                stringSave = str(output)
                f.write(stringSave)
                dictLoaded = ast.literal_eval(stringSave)
                if type(dictLoaded) is not dict: print("*TRAIN")
                f.write("\n")
        fileName = "./feverous_dev.jsonl"
        with open(fileName, 'w') as f:
            for output in feverousDev:
                stringSave = str(output)
                f.write(stringSave)
                dictLoaded = ast.literal_eval(stringSave)
                if type(dictLoaded) is not dict: print("*DEV")
                f.write("\n")
        print("Files exported.")

    def test_feverous_load_colab(self):
        fileName = "./feverous_train.jsonl"
        f = open(fileName)
        examples = []
        for line in f:
            example = ast.literal_eval(line)
            examples.append(example)
        f.close()
        count = 0
        for example in examples:
            parsed = isinstance(example, dict)
            if parsed:
                count += 1
                claim = example['claim']
                label = example['label']
                evidence = example['evidence']
                evidenceContext = example['evidence_ctxt']
                title = example['title']






