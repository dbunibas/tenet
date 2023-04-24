from src import Constants
import openai
import sys
import json
import time
import unicodedata
import re

from src.textGeneration.ParserEvidenceGenerator import parseTables

## GLOBAL VARS
USED_TOKENS = 0
TOTAL_TIME = 0
EXAMPLES_TO_GENERATE = 1000

def cleanCellValue(string):
    # return re.sub(r"\[\[[^\|]*\|", "", str(string)).replace(']]', '').replace('[[', '')
    stringClean = unicodedata.normalize('NFKD', str(
        string)).encode('ascii', 'ignore').decode("ascii")
    regexPipe = r"\w*\|"
    return re.sub(regexPipe, "", str(stringClean), 0, re.MULTILINE).replace(("["), "").replace("]", "").replace("\n", " ").strip()

def loadCache():
    try:
        cacheFile = Constants.CACHE_DIR + "chatgpt-cache.json"
        f = open(cacheFile)
        data = json.load(f)
        f.close()
        return data
    except FileNotFoundError as e:
        print(f"File not found!" + cacheFile, file=sys.stderr)
        return {}

def saveCache(cache):
    cacheFile = Constants.CACHE_DIR + "chatgpt-cache.json"
    json_object = json.dumps(cache, indent=4)
    with open(cacheFile, "w") as outfile:
        outfile.write(json_object)

def loadOutput(fileName):
    try:
        f = open(fileName)
        data = json.load(f)
        f.close()
        return data
    except FileNotFoundError as e:
        print(f"File not found! " + fileName, file=sys.stderr)
        return []

def saveOutput(output, fileOut):
    json_object = json.dumps(output, indent=4)
    with open(fileOut, "w") as outfile:
        outfile.write(json_object)

def printHeader(headers):
    headerRow = ""
    for header in headers:
        headerRow += cleanCellValue(header.name) + " | "
    return headerRow

def printRow(row):
    stringRow = ""
    for cell in row:
        stringRow += cleanCellValue(cell.value) + " | "
    return stringRow

def tableBoundaries(database, tableName):
    table = database.getTableByName(tableName)
    startHeader = 1
    endHeader = len(table.schema)
    startRow = 1
    endRow = len(table.rows)
    if endHeader < startHeader and endRow < startRow:
        return None, None, None, None
    else:
        return startHeader, endHeader, startRow, endRow

def printTable(database, tableName):
    startHeader, endHeader, startRow, endRow = tableBoundaries(database, tableName)
    table = database.getTableByName(tableName)
    output = '';
    if startHeader is None: return output
    output += "Table: " + tableName + "\n"
    output += "----------- COLUMNS (from 1 to " + str(endHeader) + ") -----------" + "\n"
    output += printHeader(table.schema) + "\n"
    output += ("----------- ROWS (from 1 to " + str(endRow) + ") -----------") + "\n"
    for row in table.rows:
        output += printRow(row) + "\n"
    return output

def generateChatGPT(database, tableName, cache):
    prompt = printTable(database, tableName)
    #print(prompt)
    response = cache.get(prompt)
    global USED_TOKENS
    global TOTAL_TIME
    if(response != None):
        USED_TOKENS += response["usedTokens"]
        TOTAL_TIME += response["time"]
        return response["response"]
    start = time.time()
    promptMessages = [
        {"role": "system",
            "content": "I give you a table and I want you to generate 3 sentences in natural language that are true and 3 sentences that are false with respect to the content of the input table. Use only the information in the table to generate the sentences. Row number starts from 1. Column number starts from 1. Return the list of cells in the table used to create each sentence. For annotations, use the following pattern: [list of rowNumber.columnNumber]"},
        {"role": "user", "content": prompt}
    ]
    openai.api_key = Constants.API_KEYS_GPT3[0]
    #openai.api_key = "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"
    chat_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=promptMessages,
        temperature=0.0
    )
    response = chat_response["choices"][0]["message"]["content"]
    usedTokens = chat_response["usage"]["total_tokens"]
    priceTokens = (usedTokens / 1000) * 0.002
    #print(response)
    #print("\nTokens:", usedTokens, "--- Price ($):", priceTokens)
    end = time.time()
    cache[prompt] = {"response": response, "usedTokens": usedTokens, "time": (end - start)}
    USED_TOKENS += usedTokens
    TOTAL_TIME += (end - start)
    saveCache(cache)
    return response

def parseSentence(sentence, database, tableName):
    # print(wiki_table.get_table_caption())
    startHeader, endHeader, startRow, endRow = tableBoundaries(database, tableName)
    result = {"sentence": "", "cells": []}
    result["sentence"] = re.sub(r'\[(.*?)\]', '', sentence).strip()
    table = database.getTableByName(tableName)
    for cellRefs in re.findall(r'\[(.*?)\]', sentence):
        # print("*" + cellRefs)
        for cellRef in cellRefs.split(","):
            cellRef = cellRef.strip()
            # print("-> " + cellRef)
            if cellRef.split(".").__len__() != 2:
                continue
            if not cellRef.split(".")[0].isdigit() or not cellRef.split(".")[1].isdigit():
                continue
            try:
                rowNum = int(cellRef.split(".")[0])
                colNum = int(cellRef.split(".")[1])
                cellID = str(rowNum) + "." + str(colNum)
                result["cells"].append(cellID)
            except Exception:
                pass
    return result


def addExample(database, tableName, exampleObj, chatgpt_output):
    example = {
        "supports": [],
        "refutes": []
    }
    sentenceType = ''
    for line in chatgpt_output.splitlines():
        if not line.strip():
            continue
        elif line.startswith("True"):
            sentenceType = 'supports'
        elif line.startswith("False"):
            sentenceType = 'refutes'
        elif line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
            parsedSentence = parseSentence(line[2:].strip(), database, tableName)
            if parsedSentence == None:
                continue
            example[sentenceType].append(parsedSentence)
        else:
            print("UNKNOWN LINE: " + line)
    exampleObj["baselineChatGPT"] = example

def execute():
    #fileInput = Constants.CACHE_DIR + "evidences_sel_3500tables_tabfact_query.json"
    #fileOutput = Constants.CACHE_DIR + "baselineChatGPT_evidences_sel_3500tables_tabfact_query.json"
    #fileInput = Constants.CACHE_DIR + "generated_infotabs_random_2000tb_5pertb_130423.json"
    #fileOutput = Constants.CACHE_DIR + "baselineChatGPT_generated_infotabs_random_2000tb_5pertb_130423.json"
    isFeverous = False  ## use False if the input file is different from FEVEROUS inputs
    inputsFile = [Constants.CACHE_DIR + "evidences_sel_3500tables_tabfact_query.json", Constants.CACHE_DIR + "generated_infotabs_random_2000tb_5pertb_130423.json"]
    outputsFile = [Constants.CACHE_DIR + "baselineChatGPT_evidences_sel_3500tables_tabfact_query.json", Constants.CACHE_DIR + "baselineChatGPT_generated_infotabs_random_2000tb_5pertb_130423.json"]

    for fileInput, fileOutput in zip(inputsFile, outputsFile):
        print("Input: ", fileInput)
        print("Output: ", fileOutput)
        output = loadOutput(fileOutput)
        output = []

        cache = loadCache()

        f = open(fileInput)
        data = json.load(f)
        pos = 0
        generated = 0
        maxLen = len(data)
        while generated < EXAMPLES_TO_GENERATE and pos < maxLen:
            example = data[pos]
            pos += 1
            originalTable = example['original_table']
            title = example['title']
            database = parseTables(originalTable, title, isFeverous)
            database.inferTypes()
            try:
                chatgpt_output = generateChatGPT(database, title, cache)
                if (chatgpt_output == None): continue
                 # print("ChatGPT Output: ", chatgpt_output)
                addExample(database,title,  example,chatgpt_output)
                generated += 1
                print("Example: ", generated, " / ", EXAMPLES_TO_GENERATE)
            except:
                pass

        saveOutput(data, fileOutput)
        global USED_TOKENS
        global TOTAL_TIME
        print("Used Tokens: ", USED_TOKENS)
        print("Price: ", (USED_TOKENS / 1000) * 0.002)
        print("Total Time (sec): ", TOTAL_TIME)
        print("Done.")

if __name__ == '__main__':
    execute()