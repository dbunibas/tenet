import json
from tqdm import tqdm

from src import Constants
from src.RunnerTextGeneration import exploreTextForStrategy
from src.textGeneration.ParserEvidenceGenerator import parseTables, parseEvidence, detect_type_table


def getType(key):
    if "filter" in key and "compute" in key:
        return "Filter+AggrFunct"
    if "compute" in key and ("min" in key or "max" in key):
        return "MinMax"
    if "compute" in key:
        return "AggrFunct"
    if "filter" in key:
        return "Filter"
    if "compare" in key:
        return "Comparison"
    return "Lookup"

def updateStats(stats, generatedSentences):
    for key in generatedSentences:
        counter = 0
        typeKey = getType(key)
        if typeKey not in stats:
            stats[typeKey] = counter
        else:
            counter = stats[typeKey]
        counter += 1
        stats[typeKey] = counter

def printStats(stats, negStats, type):
    print(type)
    print("POSITIVE")
    for key, value in stats.items():
        print(key, value)
    print("NEGATIVE")
    for key, value in negStats.items():
        print(key, value)

def printGeneratedSentences(generated, database, title, stats, negstats, print=True):
    for gen in generated:
        if "chatGPT" in gen:
            sentences = gen["chatGPT"]
            evidenceFromFile = gen['table']
            evidence = parseEvidence(evidenceFromFile, title, database)
            if print:
                print("*** DB: \n", database)
                print("*** EVIDENCE: \n", evidence)
                print("*** Sentences:\n", sentences)
            updateStats(stats, sentences)
        if "neg_chatGPT" in gen:
            sentences = gen["neg_chatGPT"]
            evidenceFromFile = gen['neg_table']
            evidence = parseEvidence(evidenceFromFile, title, database)
            if print:
                print("*** DB: \n", database)
                print("*** NEG EVIDENCE: \n", evidence)
                print("*** Neg Sentences:\n", sentences)
            updateStats(negstats, sentences)


if __name__ == '__main__':
    operations = [Constants.OPERATION_LOOKUP, Constants.OPERATION_COMPARISON, Constants.OPERATION_FILTER,
                  Constants.OPERATION_MIN, Constants.OPERATION_MAX, Constants.OPERATION_COUNT,
                  Constants.OPERATION_SUM, Constants.OPERATION_AVG]
    comparisons = [Constants.OPERATOR_SAME, Constants.OPERATOR_LT, Constants.OPERATOR_GT]
    fileInput = Constants.CACHE_DIR + "evidences_g5_s300_270323_r_cr_q.json"
    fileOutput = Constants.CACHE_DIR + "output_evidences_g5_s300_270323_r_cr_q.json"
    f = open(fileInput)
    data = json.load(f)
    explored = []
    print("Exploring the data")
    skippedTables = 0
    maxTables = 500 ## None for the full file
    printSentences = False
    if maxTables is not None:
        data = data[0: maxTables]
    for example in tqdm(data):
    #for example in data:
        original_claim = example['original_claim']
        #print("ORIG CLAIM: ", original_claim)
        originalTable = example['original_table']
        title = example['title']
        database = parseTables(originalTable, title)
        database.inferTypes()
        if not database.containsNonEmptyTables():
            transposed = list(map(list, zip(*originalTable)))
            database = parseTables(transposed, title)
            database.inferTypes()
        if not database.containsNonEmptyTables():
            skippedTables += 1
        #print("*** DATABASE:", database)
        generated_query = example['generated_query']
        #print("** Generated-query")
        pgenerated, ngenerated = exploreTextForStrategy(generated_query, database, title, operations, comparisons)
        generated_random = example['generated_random']
        #print("** Generated-random")
        pgenerated_random, ngenerated_random = exploreTextForStrategy(generated_random, database, title, operations, comparisons)
        #generateTextForStrategy(generated_random, database, explored)
        generated_coldrandom = example['generated_coldrandom']
        #print("** Generated-coldrandom")
        pgenerated_coldrandom, ngenerated_coldrandom = exploreTextForStrategy(generated_coldrandom, database, title, operations, comparisons)
        #generateTextForStrategy(generated_coldrandom, database, explored)

    print("*** Skipped Tables: ", skippedTables)

    f = open(fileOutput)
    data = json.load(f)
    statsQuery = dict()
    negStatsQuery = dict()
    statsRandom = dict()
    negStatsRandom = dict()
    statsColdRandom = dict()
    negStatsColdRandom = dict()
    for example in data:
        original_claim = example['original_claim']
        originalTable = example['original_table']
        title = example['title']
        database = parseTables(originalTable, title)
        database.inferTypes()
        if not database.containsNonEmptyTables():
            transposed = list(map(list, zip(*originalTable)))
            database = parseTables(transposed, title)
            database.inferTypes()
        generated_query = example['generated_query']
        generated_random = example['generated_random']
        generated_coldrandom = example['generated_coldrandom']
        #print("** Generated-query")
        printGeneratedSentences(generated_query, database, title, statsQuery, negStatsQuery, print=printSentences)
        #print("** Generated-random")
        printGeneratedSentences(generated_random, database, title, statsRandom, negStatsRandom, print=printSentences)
        #print("** Generated-coldrandom")
        printGeneratedSentences(generated_coldrandom, database, title, statsColdRandom, negStatsColdRandom, print=printSentences)
    print("** Stats Generated-query")
    printStats(statsQuery, negStatsQuery, "Query")
    print("** Stats Generated-Random")
    printStats(statsRandom, negStatsRandom, "Random")
    print("** Stats Generated-ColdRandom")
    printStats(statsColdRandom, negStatsColdRandom, "ColdRandom")


