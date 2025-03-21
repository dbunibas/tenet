## TODO: change with your API_KEY
CACHE_DIR = "/usr/src/app/data"

LANGUAGE_MODEL_CHAT_GTP = "ChatGPT"
LANGUAGE_MODEL_GPT3 = "GPT3"
LANGUAGE_MODEL_T5 = "T5"
LANGUAGE_MODEL_CHAT_GTP_ERRORS = ["There is no data.", "FAILED"]
LANGUAGE_MODEL_MISTRAL_OLLAMA = "MistralOllama"
LANGUAGE_MODEL_MISTRAL_TOGETHER_AI = "MistralTogetherAi"

## ATTRIBUTE TYPE
NUMERICAL = "numerical"
CATEGORICAL = "categorical"

## OPERATIONS NAME
OPERATION_LOOKUP = "lookup"
OPERATION_COMPARISON = "comparison"
OPERATION_MIN = "min"
OPERATION_MAX = "max"
OPERATION_COUNT = "count"
OPERATION_GROUPING = "grouping"
OPERATION_SUM = "sum"
OPERATION_AVG = "avg"
OPERATION_FILTER = "filter"
OPERATION_RANKED = "ranked"
OPERATION_PERCENTAGE = "percentage"
OPERATION_COMBINED = "combined"

## OPERATORS
OPERATOR_GT = ">"
OPERATOR_LT = "<"
OPERATOR_SAME = "="

## VALUE GENERATOR
STRATEGY_ACTIVE_DOMAIN = "ActiveDomain"
STRATEGY_LM_GENERATOR = "LMGenerator"
STRATEGY_CHANGE_MIN = "ChangeMin"
STRATEGY_CHANGE_MAX = "ChangeMax"

## STATISTICS
STATISTICS_TOTAL_TIME_POSITIVE = "total_time_positive"
STATISTICS_TOTAL_TIME_NEGATIVE = "total_time_negative"
STATISTICS_TOTAL_NEGATIVE_INSTANCES = "total_time_negative_instances"
STATISTICS_EVIDENCE_GENERATION = "total_time_evidence_generation"
STATISTICS_EVIDENCE_GENERATION_POSITIVE = "total_time_evidence_generation_positive"
STATISTICS_EVIDENCE_GENERATION_NEGATIVE = "total_time_evidence_generation_negative"
STATISTICS_S_QUERIES_DISCOVERY = "total_time_s_queries_discovery"
STATISTICS_S_QUERIES_DISCOVERY_POSITIVE = "total_time_s_queries_discovery_positive"
STATISTICS_S_QUERIES_DISCOVERY_NEGATIVE = "total_time_s_queries_discovery_negative"
STATISTICS_TEXT_GENERATION = "total_time_text_generation"
STATISTICS_TEXT_GENERATION_POSITIVE = "total_time_text_generation_positive"
STATISTICS_TEXT_GENERATION_NEGATIVE = "total_time_text_generation_negative"
STATISTICS_USED_TOKENS = "used_tokens_chatGPT"
