from src.Constants import STATISTICS_TOTAL_TIME_POSITIVE, STATISTICS_TOTAL_TIME_NEGATIVE, \
    STATISTICS_EVIDENCE_GENERATION, STATISTICS_S_QUERIES_DISCOVERY, STATISTICS_TEXT_GENERATION, \
    STATISTICS_TOTAL_NEGATIVE_INSTANCES, STATISTICS_USED_TOKENS, STATISTICS_EVIDENCE_GENERATION_POSITIVE, \
    STATISTICS_EVIDENCE_GENERATION_NEGATIVE, \
    STATISTICS_S_QUERIES_DISCOVERY_NEGATIVE, STATISTICS_S_QUERIES_DISCOVERY_POSITIVE, \
    STATISTICS_TEXT_GENERATION_NEGATIVE, STATISTICS_TEXT_GENERATION_POSITIVE, OPERATION_LOOKUP, OPERATION_COMPARISON, \
    OPERATION_FILTER, OPERATION_MAX, OPERATION_MIN, OPERATION_COUNT, OPERATION_SUM, OPERATION_AVG, OPERATION_RANKED, \
    OPERATION_PERCENTAGE, OPERATION_COMBINED


class Statistics:

    def __init__(self):
        self.data = {}
        self.data[STATISTICS_TOTAL_TIME_POSITIVE] = 0
        self.data[STATISTICS_TOTAL_TIME_NEGATIVE] = 0
        self.data[STATISTICS_EVIDENCE_GENERATION] = 0
        self.data[STATISTICS_EVIDENCE_GENERATION_POSITIVE] = 0
        self.data[STATISTICS_EVIDENCE_GENERATION_NEGATIVE] = 0
        self.data[STATISTICS_S_QUERIES_DISCOVERY] = 0
        self.data[STATISTICS_S_QUERIES_DISCOVERY_POSITIVE] = 0
        self.data[STATISTICS_S_QUERIES_DISCOVERY_NEGATIVE] = 0
        self.data[STATISTICS_TEXT_GENERATION] = 0.0
        # self.data[STATISTICS_TEXT_GENERATION_POSITIVE] = 0.0
        # self.data[STATISTICS_TEXT_GENERATION_NEGATIVE] = 0.0
        self.data[STATISTICS_TOTAL_NEGATIVE_INSTANCES] = 0.0
        self.data[STATISTICS_USED_TOKENS] = 0
        # operations = [OPERATION_LOOKUP, OPERATION_COMPARISON, OPERATION_FILTER, OPERATION_MIN, OPERATION_MAX, OPERATION_COUNT,
        #              OPERATION_SUM, OPERATION_AVG,OPERATION_RANKED, OPERATION_PERCENTAGE, OPERATION_COMBINED]
        # for op in operations:
        #    self.data[op] = 0

    def addOrUpdate(self, key, value):
        if key not in self.data:
            self.data[key] = value
        else:
            prevVal = self.data[key]
            prevVal += value
            self.data[key] = prevVal

    def print(self):
        for key, value in self.data.items():
            print(key, value)
