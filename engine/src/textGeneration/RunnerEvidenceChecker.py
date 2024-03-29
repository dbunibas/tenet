from src import Constants
from src.textGeneration.EvidenceChecker import checkEvidence, checkEvidenceForComparison, checkEvidenceForGrouping
from src.textGeneration.ParserEvidenceGenerator import *
import json


def findAllowedOperations(evidence, database, ops, comparisons):
    allowedOP = []
    for op in ops:
        check = checkEvidence(evidence, database, op)
        if check:
            if op not in [Constants.OPERATION_COMPARISON, Constants.OPERATION_GROUPING]:
                allowedOP.append(op)
            elif op in [Constants.OPERATION_COMPARISON]:
                for operator in comparisons:
                    if checkEvidenceForComparison(evidence, database, operator):
                        allowedOP.append((op + "_" + operator))
            else:
                for operator in comparisons:
                    check, attribute, value = checkEvidenceForGrouping(evidence, database, operator)
                    if check:
                        allowedOP.append((op + "_" + operator + " " + str(value) + "_" + attribute))
    return allowedOP


if __name__ == '__main__':
    f = open('../../data/claims_for_enzo_301122.json')
    ops = [Constants.OPERATION_MIN, Constants.OPERATION_MAX, Constants.OPERATION_COUNT, Constants.OPERATION_LOOKUP,
           Constants.OPERATION_COMPARISON, Constants.OPERATION_GROUPING]
    comparisons = [Constants.OPERATOR_LT, Constants.OPERATOR_GT, Constants.OPERATOR_SAME]
    data = json.load(f)
    for dict in data:
        # print(dict.keys())
        generated = dict['generated']
        originalOne = dict['original_one']
        title = dict['title']
        originalTable = dict['original_table']
        claimType = dict['claim_type']
        database = parseTables(originalTable, title)
        database.inferTypes()
        if len(generated) > 0:
            print(title)
            print(claimType)
            print(database)
        for gen in generated:
            evidenceFromFile = gen['table']
            evidence = parseEvidence(evidenceFromFile)
            print("Evidence")
            print(evidence)
            allowedOP = findAllowedOperations(evidence, database, ops, comparisons)
            print("Operations:", allowedOP)
            negativeEvidence = gen['neg_table']
            negEvidence = parseEvidence(negativeEvidence)
            print("Neg Evidence")
            print(negEvidence)
            negativeAllowedOP = findAllowedOperations(negEvidence, database, ops, comparisons)
            print("Operations:", negativeAllowedOP)
            print("#" * 30)
        print("*" * 30)
