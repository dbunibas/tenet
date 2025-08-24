from src import Constants
from src.LoggedDecorators import timed
from src.model.ColdSearch import ColdSearch
from src.model.OperatorAggregativeFunction import OperatorAggregativeFunction
from src.model.OperatorComparison import OperatorComparison
from src.model.OperatorFilter import OperatorFilter
from src.model.OperatorFinder import OperatorFinder
from src.model.OperatorLookup import OperatorLookup
from src.model.OperatorMinMax import OperatorMinMax
from src.model.OperatorPercentage import OperatorPercentage
from src.model.OperatorRanked import OperatorRanked
from src.model.OperatorRankedSimple import OperatorRankedSimple
from src.model.RefuteInstancesGenerator import RefuteInstancesGenerator
from src.model.RelationalTable import Evidence
from src.model.WarmSearch import WarmSearch
from src.textGeneration.ChatGPTLanguageModel import ChatGPTLanguageModel
from src.textGeneration.GenericTogetherAILanguageModel import GenericgetherAILanguageModel
from src.textGeneration.LLama3TogetherAILanguageModel import LLama3TogetherAILanguageModel
from src.textGeneration.ExaoneTogetherAILanguageModel import ExaoneTogetherAILanguageModel
from src.textGeneration.MistralOllamaLanguageModel import MistralOllamaLanguageModel
from src.textGeneration.MistralTogetherAILanguageModel import MistralTogetherAILanguageModel
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
import functools
import time
import logging

logger = logging.getLogger(__name__)
# Misc logger setup so a debug log statement gets printed on stdout.
logger.setLevel("DEBUG")


class Tenet:

    def __init__(self, database, seed, operations, comparisons, bestEvidences, sentencesPerExample, languageModel,
                 rateLimit, sleepTime, address=None):
        ## DATABASE
        self.database = database
        ## EVIDENCE DISCOVERY
        self.coldSearch = ColdSearch()
        self.warmSearch = WarmSearch()
        self.seed = seed
        self.coldSearch.setSeed(seed)
        self.warmSearch.setSeed(seed)
        ## TEXT GENERATION
        self.model = None
        self.operations = operations
        # self.operations = [Constants.OPERATION_LOOKUP, Constants.OPERATION_COMPARISON, Constants.OPERATION_FILTER,
        #              Constants.OPERATION_MIN, Constants.OPERATION_MAX, Constants.OPERATION_COUNT,
        #              Constants.OPERATION_SUM, Constants.OPERATION_AVG, Constants.OPERATION_RANKED, Constants.OPERATION_PERCENTAGE]
        # self.comparisons = [Constants.OPERATOR_SAME, Constants.OPERATOR_LT, Constants.OPERATOR_GT]
        self.comparisons = comparisons
        self.languageModel = languageModel
        self.initLanguageModel(rateLimit, sleepTime, address)
        self.bestEvidences = bestEvidences
        self.sentencesPerExample = sentencesPerExample
        ## REFUTES EXAMPLE GENERATION
        self.refutesInstancesGenerator = RefuteInstancesGenerator()
        if seed is not None:
            self.refutesInstancesGenerator.setSeed(seed)
        self.statistics = None

    # @timed
    def initLanguageModel(self, rateLimit, sleepTime, address):
        if self.languageModel == Constants.LANGUAGE_MODEL_CHAT_GTP:
            self.model = ChatGPTLanguageModel()
            self.model.rateLimit = rateLimit
            self.model.sleepTime = sleepTime
            self.model.enableGPT = True
            return
        if self.languageModel == Constants.LANGUAGE_MODEL_MISTRAL_OLLAMA:
            self.model = MistralOllamaLanguageModel(address)
            return
        if self.languageModel == Constants.LANGUAGE_MODEL_MISTRAL_TOGETHER_AI:
            self.model = MistralTogetherAILanguageModel()
            return
        if self.languageModel == Constants.LANGUAGE_MODEL_LLAMA3_TOGETHER_AI:
            self.model = LLama3TogetherAILanguageModel()
            return
        if self.languageModel == Constants.LANGUAGE_MODEL_EXAONE_TOGETHER_AI:
            self.model = ExaoneTogetherAILanguageModel()
            return
        self.model = GenericgetherAILanguageModel(self.languageModel)

    def disableLanguageModel(self):
        self.model.enableGPT = False

    # @timed
    def generatePositiveExamples(self, tableName, evidenceSel, numEvidence):
        table = self.database.getTableByName(tableName)
        start = time.time()
        examples = self.generateExamples(table, evidenceSel, numEvidence, True)
        end = time.time()
        if self.statistics is not None: self.statistics.data[Constants.STATISTICS_TOTAL_TIME_POSITIVE] += (end - start)
        return examples

    # @timed
    def generateNegativeExamples(self, tableName, evidenceSel, numEvidence, addRows, rowsToAdd, removeRows,
                                 rowsToRemove, strategy, useLM=False, instanceRefute=None):
        table = self.database.getTableByName(tableName)
        if useLM: self.refutesInstancesGenerator.useLM()
        start = time.time()
        # print("*** Generate Negative Instance")
        refuteInstances = None
        if instanceRefute is not None:
            refuteInstances = instanceRefute
        else:
            if len(table.rows) > 1:
                refuteInstances = self.refutesInstancesGenerator.generateInstanceForRefuteBigTables(table, addRows,
                                                                                                    rowsToAdd,
                                                                                                    removeRows,
                                                                                                    rowsToRemove,
                                                                                                    strategy,
                                                                                                    evidenceSel)
            else:
                refuteInstances = self.refutesInstancesGenerator.generateInstanceForRefute(table, addRows, rowsToAdd,
                                                                                           removeRows, rowsToRemove,
                                                                                           strategy, evidenceSel)
        end1 = time.time()
        if self.statistics is not None: self.statistics.data[Constants.STATISTICS_TOTAL_NEGATIVE_INSTANCES] += (
                    end1 - start)
        examples = self.generateExamples(refuteInstances, evidenceSel, numEvidence, False, originalTable=table)
        end2 = time.time()
        if self.statistics is not None: self.statistics.data[Constants.STATISTICS_TOTAL_TIME_NEGATIVE] += (end2 - start)
        ## Change the refuteInstances with the original one
        for ex in examples:
            ex["table"] = table
        # print("*** Neg Examples:", len(examples))
        return examples

    # @timed
    # @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(10))
    def generateExamples(self, table, evidenceSel, numEvidence, isPositive, originalTable=None):
        ## New Evidence Discovery
        evidences = []
        start = time.time()
        if evidenceSel is None:
            evidences = self.coldSearch.findEvidences(table, numEvidence, evidenceSel)
        else:
            evidences, query, attrMapping = self.warmSearch.findEvidences(table, numEvidence, evidenceSel)  # Per positive
        end = time.time()
        if self.statistics is not None:
            self.statistics.data[Constants.STATISTICS_EVIDENCE_GENERATION] += (end - start)
            if isPositive:
                self.statistics.data[Constants.STATISTICS_EVIDENCE_GENERATION_POSITIVE] += (end - start)
            else:
                self.statistics.data[Constants.STATISTICS_EVIDENCE_GENERATION_NEGATIVE] += (end - start)
        # print("*** New Evidences Generated: ", len(evidences))
        ## Semantic Discovery
        start = time.time()
        positives = []
        for evidence in evidences:
            ## check if the evidence is the same as evidenceSel
            finder = OperatorFinder(evidence, self.database, self.operations, self.comparisons)
            finder.setStatistics(self.statistics)
            finder.exploreAll()
            t = (evidence, finder.allowedOperations)
            positives.append(t)
            # print("Explored with finder")
        # print("Explored all the generated evidences...rank them")
        ## Rank the best top "evidences" with more different semantics
        positives = sorted(positives, key=functools.cmp_to_key(self.importance), reverse=True)
        positiveForText = []
        if self.bestEvidences is None:
            positiveForText.append(positives[0])
        else:
            for p in positives[0:self.bestEvidences]:
                positiveForText.append(p)
        ## Text Generation with a PLM
        end = time.time()
        if self.statistics is not None:
            self.statistics.data[Constants.STATISTICS_S_QUERIES_DISCOVERY] += (end - start)
            if isPositive:
                self.statistics.data[Constants.STATISTICS_S_QUERIES_DISCOVERY_POSITIVE] += (end - start)
            else:
                self.statistics.data[Constants.STATISTICS_S_QUERIES_DISCOVERY_NEGATIVE] += (end - start)
        examples = []
        for t in positiveForText:
            evidence = t[0]
            allowedOperations = t[1]
            allowedOperations = sorted(allowedOperations, key=functools.cmp_to_key(self.compareOperators), reverse=True)
            operations = []
            if len(allowedOperations) >= self.sentencesPerExample:
                for i in range(0, self.sentencesPerExample - 1):
                    operations.append(allowedOperations[i])
                for op in allowedOperations:
                    if op.__class__.__name__ == OperatorLookup.__name__ and op not in operations:
                        operations.append(op)
                        break
            else:
                operations = allowedOperations
            for op in operations:
                task = op.printOperator(evidence, self.database)
                prompt = self.model.generatePrompt(evidence, task)
                try:
                    if self.statistics is not None: self.model.setStatistics(self.statistics)
                    sentences = self.model.generateText(prompt)
                    evidenceForExample = evidence
                    if not isPositive and evidenceSel is not None:  ## WARM, we are using the provided evidence
                        evidenceForExample = evidenceSel
                    if not isPositive:
                        evidenceForExample = self.getOriginalEvidenceFromNegative(evidenceForExample, originalTable)
                    example = {
                        "evidence": evidenceForExample,
                        "sentences": sentences,
                        "table": table,
                        "prompt": prompt,
                        "s-operation": op
                    }
                    examples.append(example)
                except Exception as e:
                    print("Error with the API: ", e)
                    print("Sleep for 10")
                    time.sleep(10)
                    # raise Exception(e) ## for exponential backoff
                    # pass ## NetworkIssues (we can log such errors or return errors)
        return examples

    def getOriginalEvidenceFromNegative(self, negativeEvidence, table):
        # originalEvidences = []
        originalEvidence = Evidence(table.tableName)
        for rowEvidence in negativeEvidence.rows:
            rowOriginal = []
            for cellEvidence in rowEvidence:
                rowPos = cellEvidence.getRowPos()
                columnPos = cellEvidence.getColumnPos()
                # log.debug("row pos: " + str(rowPos))
                # log.debug("Rows in table: " + str(table.getRowNumber()))
                if (rowPos < table.getRowNumber()):
                    originalCell = table.getCellByPos(rowPos, columnPos)
                    rowOriginal.append(originalCell)
            if len(rowOriginal) > 0: originalEvidence.addRow(rowOriginal)
        originalEvidence.build()
        # originalEvidences.append(originalEvidence)
        return originalEvidence

    def containsInstance(self, l, operatorClassNames):
        for op in l:
            if op.__class__.__name__ in operatorClassNames: return True
        return False

    def containsAggregativeOp(self, l, operation):
        for op in l:
            if op.__class__.__name__ == OperatorAggregativeFunction.__name__:
                if op.function == operation: return True
        return False

    def containsAggregativeWithfilter(self, l, operation):
        for op in l:
            if op.__class__.__name__ == OperatorAggregativeFunction.__name__:
                if op.function == operation and op.isWithFilter(): return True
        return False

    def rarityScore(self, l):
        if self.containsInstance(l, [OperatorRanked.__name__]): return 11
        if self.containsInstance(l, [OperatorMinMax.__name__]): return 10
        if self.containsInstance(l, [OperatorAggregativeFunction.__name__]):
            if self.containsAggregativeWithfilter(l, Constants.OPERATION_AVG): return 9
            if self.containsAggregativeWithfilter(l, Constants.OPERATION_SUM): return 8
            if self.containsAggregativeWithfilter(l, Constants.OPERATION_COUNT): return 7
            if self.containsAggregativeOp(l, Constants.OPERATION_AVG): return 6
            if self.containsAggregativeOp(l, Constants.OPERATION_SUM): return 5
            return 4
        if self.containsInstance(l, [OperatorPercentage.__name__]): return 2
        if self.containsInstance(l, [OperatorFilter.__name__]): return 1
        # if containsInstance(l, [OperatorMinMax.__name__, OperatorAggregativeFunction.__name__, OperatorFilter.__name__]): return 1
        if self.containsInstance(l, [OperatorRankedSimple.__name__]): return 1.5
        if self.containsInstance(l, [OperatorComparison.__name__]): return 0
        return -1

    def importance(self, t1, t2):
        operations1 = t1[1]
        operations2 = t2[1]
        # print("OP1: ", operations1)
        # print("OP2: ", operations2)
        r1Score = self.rarityScore(operations1)
        r2Score = self.rarityScore(operations2)
        ## TODO: use op.getScore():
        # print("R1 Score: ", r1Score, " R2 Score", r2Score)
        if r1Score == r2Score:
            len1 = len(operations1)
            len2 = len(operations2)
            # print("Len1: ", len1, "Len2:", len2)
            return len1 - len2
        else:
            return r1Score - r2Score

    def compareOperators(self, op1, op2):
        s1 = self.rarityScore([op1])
        s2 = self.rarityScore([op2])
        return s1 - s2

    def setStatistics(self, statisticsObs):
        ## to debug time
        self.statistics = statisticsObs
