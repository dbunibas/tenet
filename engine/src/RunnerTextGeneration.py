import functools
from functools import cmp_to_key

from src import Constants
import json
import io
from tqdm import tqdm
import time
import traceback

from src.LoggedDecorators import timed
from src.model.OperatorAggregativeFunction import OperatorAggregativeFunction
from src.model.OperatorCombined import OperatorCombined
from src.model.OperatorComparison import OperatorComparison
from src.model.OperatorFilter import OperatorFilter
from src.model.OperatorFinder import OperatorFinder
from src.model.OperatorLookup import OperatorLookup
from src.model.OperatorMinMax import OperatorMinMax
from src.model.OperatorRankedSimple import OperatorRankedSimple
from src.model.OperatorPercentage import OperatorPercentage
from src.textGeneration.ChatGPTLanguageModel import ChatGPTLanguageModel
from src.textGeneration.ParserEvidenceGenerator import parseTables, parseEvidence


def populateExplored(explored, positive, negative, maxPerTable=None):
    if len(positive) > 0:
        if maxPerTable is None:
            explored.append(positive[0])
        else:
            for p in positive[0:maxPerTable]:
                explored.append(p)
    if len(negative) > 0:
        if maxPerTable is None:
            explored.append(negative[0])
        else:
            for n in negative[0:maxPerTable]:
                explored.append(n)


def containsInstance(l, operatorClassNames):
    for op in l:
        if op.__class__.__name__ in operatorClassNames: return True
    return False


def containsAggregativeOp(l, operation):
    for op in l:
        if op.__class__.__name__ == OperatorAggregativeFunction.__name__:
            if op.function == operation: return True
    return False


def containsAggregativeWithfilter(l, operation):
    for op in l:
        if op.__class__.__name__ == OperatorAggregativeFunction.__name__:
            if op.function == operation and op.isWithFilter(): return True
    return False


def rarityScore(l):
    if containsInstance(l, [OperatorCombined.__name__]): return l[0].getScore()
    if containsInstance(l, [OperatorMinMax.__name__]): return 10
    if containsInstance(l, [OperatorAggregativeFunction.__name__]):
        if containsAggregativeWithfilter(l, Constants.OPERATION_AVG): return 9
        if containsAggregativeWithfilter(l, Constants.OPERATION_SUM): return 8
        if containsAggregativeWithfilter(l, Constants.OPERATION_COUNT): return 7
        if containsAggregativeOp(l, Constants.OPERATION_AVG): return 6
        if containsAggregativeOp(l, Constants.OPERATION_SUM): return 5
        return 4
    if containsInstance(l, [OperatorFilter.__name__]): return 1
    # if containsInstance(l, [OperatorMinMax.__name__, OperatorAggregativeFunction.__name__, OperatorFilter.__name__]): return 1
    if containsInstance(l, [OperatorRankedSimple.__name__]): return 1.5
    if containsInstance(l, [OperatorPercentage.__name__]): return 0.5
    if containsInstance(l, [OperatorComparison.__name__]): return 0
    return -1


def importance(t1, t2):
    operations1 = t1[1]
    operations2 = t2[1]
    # print("OP1: ", operations1)
    # print("OP2: ", operations2)
    r1Score = rarityScore(operations1)
    r2Score = rarityScore(operations2)
    # print("R1 Score: ", r1Score, " R2 Score", r2Score)
    if r1Score == r2Score:
        len1 = len(operations1)
        len2 = len(operations2)
        # print("Len1: ", len1, "Len2:", len2)
        return len1 - len2
    else:
        return r1Score - r2Score


def compareOperators(op1, op2):
    s1 = rarityScore([op1])
    s2 = rarityScore([op2])
    return s1 - s2


def filterExplored(explored, sentencesPerExample, model):
    print("Pick operators for selected")
    filtered = []  ## list of (task, prompt, gen, negative, operator, database)
    for example in tqdm(explored):
        evidence = example[0]
        allowedOperations = example[1]
        database = example[2]
        gen = example[3]
        positive = example[4]
        allowedOperations = sorted(allowedOperations, key=functools.cmp_to_key(compareOperators), reverse=True)
        operations = []
        if len(allowedOperations) >= sentencesPerExample:
            for i in range(0, sentencesPerExample - 1):
                operations.append(allowedOperations[i])
            for op in allowedOperations:
                if op.__class__.__name__ == OperatorLookup.__name__ and op not in operations:
                    operations.append(op)
                    break
        else:
            operations = allowedOperations
        for op in operations:
            task = op.printOperator(evidence, database)
            prompt = model.generatePrompt(evidence, task)
            current = (task, prompt, gen, positive, op, database)
            filtered.append(current)
    return filtered


def exploreOutput(evidence, database, operations, comparisons, model, gen, explored, negative=False):
    finder = OperatorFinder(evidence, database, operations, comparisons)
    finder.exploreAll()
    for operator in finder.allowedOperations:
        task = operator.printOperator(evidence, database)
        prompt = model.generatePrompt(evidence, task)
        current = (task, prompt, gen, negative, operator, database)
        explored.append(current)


def generateOutputFromExplored(explored, model):
    print("Generate the text using the Language Model")
    counterPositive = 0
    counterNegative = 0
    for task, prompt, gen, positive, operator, database in tqdm(explored):
        try:
            sentences = model.generateText(prompt)
            table = prompt.split("Table: ")[-1]
            # print(task, positive)
            # print(sentences)
            # print(table)
            # print(gen)
            # print("*************")
            outputs = {}
            if not positive:
                if 'neg_chatGPT' in gen:
                    outputs = gen['neg_chatGPT']
                else:
                    gen['neg_chatGPT'] = outputs
                if not outputs: counterNegative += 1
            else:
                if 'chatGPT' in gen:
                    outputs = gen['chatGPT']
                else:
                    gen['chatGPT'] = outputs
                if not outputs: counterPositive += 1
            outputs[task] = sentences
        except:
            time.sleep(10)
            print("Exception:", task)
            # traceback.print_exc()
            # break
    print("Positive:", counterPositive)
    print("Negative:", counterNegative)


def generateOutput(evidence, database, operations, comparisons, model, gen, explored, negative=False):
    finder = OperatorFinder(evidence, database, operations, comparisons)
    finder.exploreAll()
    # for operator in tqdm(finder.allowedOperations):
    outputs = {}
    for operator in finder.allowedOperations:
        task = operator.printOperator(evidence, database)
        prompt = model.generatePrompt(evidence, task)
        current = (task, prompt, gen, negative)
        explored.append(current)
        sentences = model.generateText(prompt)
        outputs[task] = sentences
    if negative:
        gen['neg_chatGPT'] = outputs
    else:
        gen['chatGPT'] = outputs


def debugPrintOperations(l):
    for elem in l:
        operations = elem[1]
        print(operations)


def generateLookupOnly(generated, title, isFeverous):
    positive = []
    negative = []
    for gen in generated:
        evidenceFromFile = gen['table']
        evidence = parseEvidence(evidenceFromFile, title, database, isFeverous, skipCheck=True)
        finder = OperatorFinder(evidence, database, [Constants.OPERATION_LOOKUP], [])
        finder.exploreAll()
        t = (evidence, finder.allowedOperations, database, gen, True)
        positive.append(t)
        #### negative
        negativeEvidence = gen['neg_table']
        negEvidence = parseEvidence(negativeEvidence, title, database, isFeverous, skipCheck=True)
        finder = OperatorFinder(negEvidence, database, [Constants.OPERATION_LOOKUP], [])
        finder.exploreAll()
        t = (negEvidence, finder.allowedOperations, database, gen, False)
        negative.append(t)
    positive = sorted(positive, key=functools.cmp_to_key(importance), reverse=True)
    negative = sorted(negative, key=functools.cmp_to_key(importance), reverse=True)
    return positive, negative


def exploreTextForStrategy(generated, database, title, operations, comparisons, isFeverous, useCombined,
                           operationsToIgnore=None):
    positive = []
    negative = []
    for gen in generated:
        evidenceFromFile = gen['table']
        evidence = parseEvidence(evidenceFromFile, title, database, isFeverous)
        if evidence is not None:
            finder = OperatorFinder(evidence, database, operations, comparisons)
            finder.exploreAll(useCombined)
            t = None
            if operationsToIgnore is None:
                t = (evidence, finder.allowedOperations, database, gen, True)
            else:
                t = (evidence, filterOperations(finder.allowedOperations, operationsToIgnore), database, gen, True)
            positive.append(t)
        negativeEvidence = gen['neg_table']
        negEvidence = parseEvidence(negativeEvidence, title, database, isFeverous)
        if negEvidence is not None:
            finder = OperatorFinder(negEvidence, database, operations, comparisons)
            finder.exploreAll(useCombined)
            t = None
            if operationsToIgnore is None:
                t = (negEvidence, finder.allowedOperations, database, gen, False)
            else:
                t = (negEvidence, filterOperations(finder.allowedOperations, operationsToIgnore), database, gen, False)
            negative.append(t)
    positive = sorted(positive, key=functools.cmp_to_key(importance), reverse=True)
    negative = sorted(negative, key=functools.cmp_to_key(importance), reverse=True)
    return positive, negative


def filterOperations(allOperations, operationsToIgnore):
    filtered = []
    for op in allOperations:
        if op.getTenetName() not in operationsToIgnore:
            filtered.append(op)
    return filtered


def generateTextForStrategy(generated, database, explored, isFeverous):
    for gen in generated:
        evidenceFromFile = gen['table']
        # print("Database:\n", database)
        evidence = parseEvidence(evidenceFromFile, title, database, isFeverous)
        if evidence is not None:
            # print("LOG-Evidence:\n", evidence)
            generateOutput(evidence, database, operations, comparisons, model, gen, explored)
        negativeEvidence = gen['neg_table']
        negEvidence = parseEvidence(negativeEvidence, title, database, isFeverous)
        if negEvidence is not None:
            # print("LOG-Neg_Evidence:\n", negEvidence)
            generateOutput(negEvidence, database, operations, comparisons, model, gen, explored, negative=True)


if __name__ == '__main__':
    #### Configuration Params
    ##########################
    ## Configuration Generator
    operations = [Constants.OPERATION_LOOKUP, Constants.OPERATION_COMPARISON, Constants.OPERATION_FILTER,
                  Constants.OPERATION_MIN, Constants.OPERATION_MAX, Constants.OPERATION_COUNT,
                  Constants.OPERATION_SUM, Constants.OPERATION_AVG,
                  Constants.OPERATION_RANKED,
                  Constants.OPERATION_PERCENTAGE]  # , Constants.OPERATION_COMBINED] ## revision
    # operationsIgnore = [Constants.OPERATION_LOOKUP, Constants.OPERATION_COMPARISON, Constants.OPERATION_FILTER,
    #              Constants.OPERATION_MIN, Constants.OPERATION_MAX, Constants.OPERATION_COUNT,
    #              Constants.OPERATION_SUM, Constants.OPERATION_AVG]
    operationsIgnore = []
    comparisons = [Constants.OPERATOR_SAME, Constants.OPERATOR_LT, Constants.OPERATOR_GT]
    useCombined = False
    languageModel = Constants.LANGUAGE_MODEL_CHAT_GTP
    ## TODO: other params for the language model
    sleepTime = 4  # in secs, use 4 with free API, otherwise set it to None or to a small value
    rateLimit = True  # set to true with free API, otherwise to False
    model = None
    generateOutput = True  # won't generate GPT output and also requests
    if languageModel == Constants.LANGUAGE_MODEL_CHAT_GTP:
        model = ChatGPTLanguageModel()
        model.rateLimit = rateLimit
        model.sleepTime = sleepTime
        model.enableGPT = True
    ## Input-Output
    # fileInput = Constants.CACHE_DIR + "generated_from_selected_070423_500tb_20pertb_newformat.json"
    fileInput = Constants.CACHE_DIR + "/revision/evidences_g5_s300_270323_r_cr_q.json"
    fileOutput = Constants.CACHE_DIR + "/revision/output_evidences_g5_s300_270323_r_cr_q.json"
    isFeverous = True  ## use False if the input file is different from FEVEROUS inputs
    tableToUse = 200
    sentencesPerExample = 3
    evidencePerExample = None  ## int value or None
    f = open(fileInput)
    data = json.load(f)
    if tableToUse is not None:
        data = data[0: tableToUse]
    explored = []
    print("Exploring the data")
    start_time = time.time()
    for example in tqdm(data):
        # for example in data:
        # original_claim = None
        # if isFeverous:
        #    original_claim = example['original_claim']
        #    #print("ORIG CLAIM: ", original_claim)
        # else:
        #    original_claim = example['generated'][0]['original_claim_fev']
        originalTable = example['original_table']
        title = example['title']
        database = parseTables(originalTable, title, isFeverous)
        database.inferTypes()
        if not database.containsNonEmptyTables():
            transposed = list(map(list, zip(*originalTable)))
            database = parseTables(transposed, title)
            database.inferTypes()
        if not database.containsNonEmptyTables():
            ## mess tables we're going for lookup only
            if isFeverous:  ## REVISION: we want to avoid to generate lookups
                generated_query = example['generated_query']
                pgenerated, ngenerated = generateLookupOnly(generated_query, title, isFeverous)  ## REVISION
                populateExplored(explored, pgenerated, ngenerated, evidencePerExample)  ## REVISION
                generated_random = example['generated_random']
                pgenerated_random, ngenerated_random = generateLookupOnly(generated_random, title,
                                                                          isFeverous)  ## REVISION
                populateExplored(explored, pgenerated_random, ngenerated_random, evidencePerExample)  ## REVISION
                generated_coldrandom = example['generated_coldrandom']
                pgenerated_coldrandom, ngenerated_coldrandom = generateLookupOnly(generated_coldrandom, title,
                                                                                  isFeverous)  ## REVISION
                populateExplored(explored, pgenerated_coldrandom, ngenerated_coldrandom,
                                 evidencePerExample)  ## REVISION
            else:
                generated_query = example['generated'][0]['generated']
                pgenerated, ngenerated = generateLookupOnly(generated_query, title)  ## REVISION
                populateExplored(explored, pgenerated, ngenerated, evidencePerExample)  ## REVISION
        else:
            if isFeverous:
                # print("*** DATABASE:", database)
                generated_query = example['generated_query']
                # print("** Generated-query")
                # pgenerated, ngenerated = exploreTextForStrategy(generated_query, database, title, operations, comparisons, isFeverous, useCombined ,operationsToIgnore=operationsIgnore)
                # populateExplored(explored, pgenerated, ngenerated, evidencePerExample)
                generated_random = example['generated_random']  ## REVISION
                # print("** Generated-random") ## REVISION
                pgenerated_random, ngenerated_random = exploreTextForStrategy(generated_random, database, title,
                                                                              operations, comparisons, isFeverous,
                                                                              useCombined,
                                                                              operationsToIgnore=operationsIgnore)  ## REVISION
                populateExplored(explored, pgenerated_random, ngenerated_random, evidencePerExample)  ## REVISION
                generated_coldrandom = example['generated_coldrandom']  ## REVISION
                # print("** Generated-coldrandom")
                # pgenerated_coldrandom, ngenerated_coldrandom = exploreTextForStrategy(generated_coldrandom, database, title, operations, comparisons, isFeverous, useCombined, operationsToIgnore=operationsIgnore) ## REVISION
                # populateExplored(explored, pgenerated_coldrandom, ngenerated_coldrandom, evidencePerExample) ## REVISION
            else:
                # print("*** DATABASE:", database)
                # generated_query = example['generated'][0]['generated']
                generated_query = example['generated']  ## REVISION % ERRORS
                # print("** Generated-query")
                pgenerated, ngenerated = exploreTextForStrategy(generated_query, database, title, operations,
                                                                comparisons, isFeverous, useCombined,
                                                                operationsToIgnore=operationsIgnore)
                populateExplored(explored, pgenerated, ngenerated, evidencePerExample)
    end_time = time.time()
    print("S-Queries exploration (sec)", (end_time - start_time))
    start_time = time.time()
    filtered = filterExplored(explored, sentencesPerExample, model)
    end_time = time.time()
    print("Filter s-queries (sec)", (end_time - start_time))
    print("Filtered:", len(filtered))
    for filter in filtered:
        task, prompt, gen, positive, op, database = filter
        # print(task)
    if generateOutput:
        generateOutputFromExplored(filtered, model)
        jsonString = json.dumps(data, indent=4)
        with io.open(fileOutput, 'w') as f:
            f.write(jsonString)
        print("Used ChatGPT-Tokens:", model.usedTokens)
        print("Estimated price ($):", model.getPrice())
        print("ChatGPT-Time Generation (sec):", model.timeElapsed)
