from src import Constants
from src.model.ColdSearch import ColdSearch
from src.model.OperatorAggregativeFunction import OperatorAggregativeFunction
from src.model.OperatorComparison import OperatorComparison
from src.model.OperatorFilter import OperatorFilter
from src.model.OperatorFinder import OperatorFinder
from src.model.OperatorLookup import OperatorLookup
from src.model.OperatorMinMax import OperatorMinMax
from src.model.RefuteInstancesGenerator import RefuteInstancesGenerator
from src.model.WarmSearch import WarmSearch
from src.textGeneration.ChatGPTLanguageModel import ChatGPTLanguageModel

import functools


class Tenet:

    def __init__(self, database, seed, operations, comparisons, bestEvidences, sentencesPerExample, languageModel, rateLimit, sleepTime):
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
        self.operations = [Constants.OPERATION_LOOKUP, Constants.OPERATION_COMPARISON, Constants.OPERATION_FILTER,
                      Constants.OPERATION_MIN, Constants.OPERATION_MAX, Constants.OPERATION_COUNT,
                      Constants.OPERATION_SUM, Constants.OPERATION_AVG]
        self.comparisons = [Constants.OPERATOR_SAME, Constants.OPERATOR_LT, Constants.OPERATOR_GT]
        self.languageModel = Constants.LANGUAGE_MODEL_CHAT_GTP
        self.initLanguageModel(rateLimit, sleepTime)
        self.bestEvidences = bestEvidences
        self.sentencesPerExample = sentencesPerExample
        ## REFUTES EXAMPLE GENERATION
        self.refutesInstancesGenerator = RefuteInstancesGenerator()
        if seed is not None:
            self.refutesInstancesGenerator.setSeed(seed)


    def initLanguageModel(self, rateLimit, sleepTime):
        if self.languageModel == Constants.LANGUAGE_MODEL_CHAT_GTP:
            self.model = ChatGPTLanguageModel()
            self.model.rateLimit = rateLimit
            self.model.sleepTime = sleepTime
            self.model.enableGPT = True

    def generatePositiveExamples(self, tableName, evidenceSel, numEvidence):
        table = self.database.getTableByName(tableName)
        return self.generateExamples(table, evidenceSel, numEvidence)

    def generateNegativeExamples(self, tableName, evidenceSel, numEvidence, addRows, rowsToAdd, removeRows, rowsToRemove, strategy, useLM=False):
        table = self.database.getTableByName(tableName)
        if useLM: self.refutesInstancesGenerator.useLM()
        refuteInstances = self.refutesInstancesGenerator.generateInstanceForRefute(table, addRows, rowsToAdd, removeRows, rowsToRemove, strategy)
        examples = self.generateExamples(refuteInstances, evidenceSel, numEvidence)
        ## Change the refuteInstances with the original one
        for ex in examples:
            ex["table"] = table
        return examples

    def generateExamples(self, table, evidenceSel, numEvidence):
        ## New Evidence Discovery
        evidences = []
        if evidenceSel is None:
            evidences = self.coldSearch.findEvidences(table, numEvidence, evidenceSel)
        else:
            evidences = self.warmSearch.findEvidences(table, numEvidence, evidenceSel)
        print("*** New Evidences Generated: ", len(evidences))
        ## Semantic Discovery
        positives = []
        for evidence in evidences:
            ## check if the evidence is the same as evidenceSel
            finder = OperatorFinder(evidence, self.database, self.operations, self.comparisons)
            finder.exploreAll()
            t = (evidence, finder.allowedOperations)
            positives.append(t)
        ## Rank the best top "evidences" with more different semantics
        positives = sorted(positives, key=functools.cmp_to_key(self.importance), reverse=True)
        positiveForText = []
        if self.bestEvidences is None:
            positiveForText.append(positives[0])
        else:
            for p in positives[0:self.bestEvidences]:
                positiveForText.append(p)
        ## Text Generation with a PLM
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
                    sentences = self.model.generateText(prompt)
                    example = {
                        "evidence": evidence,
                        "sentences": sentences,
                        "table": table,
                        "prompt": prompt,
                        "s-operation": op
                    }
                    examples.append(example)
                except Exception as e:
                    print("Error with the API: ", e)
                    pass ## NetworkIssues (we can log such errors or return errors)
        return examples


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
        if self.containsInstance(l, [OperatorMinMax.__name__]): return 10
        if self.containsInstance(l, [OperatorAggregativeFunction.__name__]):
            if self.containsAggregativeWithfilter(l, Constants.OPERATION_AVG): return 9
            if self.containsAggregativeWithfilter(l, Constants.OPERATION_AVG): return 8
            if self.containsAggregativeWithfilter(l, Constants.OPERATION_COUNT): return 7
            if self.containsAggregativeOp(l, Constants.OPERATION_AVG): return 6
            if self.containsAggregativeOp(l, Constants.OPERATION_SUM): return 5
            return 4
        if self.containsInstance(l, [OperatorFilter.__name__]): return 1
        # if containsInstance(l, [OperatorMinMax.__name__, OperatorAggregativeFunction.__name__, OperatorFilter.__name__]): return 1
        if self.containsInstance(l, [OperatorComparison.__name__]): return 0
        return -1

    def importance(self, t1, t2):
        operations1 = t1[1]
        operations2 = t2[1]
        # print("OP1: ", operations1)
        # print("OP2: ", operations2)
        r1Score = self.rarityScore(operations1)
        r2Score = self.rarityScore(operations2)
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

