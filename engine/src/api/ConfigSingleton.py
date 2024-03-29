import os
import logging
import json
import time
from pathlib import Path

from src import Constants

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class ConfigSingleton(object):

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ConfigSingleton, cls).__new__(cls)
            configPath = "." + os.path.sep + "data" + os.path.sep + "config.json"
            log.info("Config Path:" + configPath)
            current_working_directory = os.getcwd()
            log.info("Current dir: " + current_working_directory)
            if os.path.exists(configPath):
                log.info("Config file found. Load configuration")
                f = open(configPath)
                configData = json.load(f)
                log.info("Loaded Configuration:")
                log.info(configData)
                f.close()
                cls.instance.CACHE_DIR = configData["CACHE_DIR"]
                cls.instance.SEED = configData["SEED"]
                configDataNegativeTableGeneration = configData["NEGATIVE_TABLE_GENERATION"]
                cls.instance.NEGATIVE_TABLE_GENERATION_ADD_ROWS = str(
                    configDataNegativeTableGeneration["addRows"]).lower == "true"
                cls.instance.NEGATIVE_TABLE_GENERATION_ROWS_TO_ADD = int(configDataNegativeTableGeneration["rowsToAdd"])
                cls.instance.NEGATIVE_TABLE_GENERATION_REMOVE_ROWS = str(
                    configDataNegativeTableGeneration["removeRows"]).lower == "true"
                cls.instance.NEGATIVE_TABLE_GENERATION_ROWS_TO_REMOVE = int(
                    configDataNegativeTableGeneration["rowsToRemove"])
                cls.instance.NEGATIVE_TABLE_GENERATION_USE_LM = str(
                    configDataNegativeTableGeneration["addRows"]).lower == "true"
                cls.instance.NEGATIVE_TABLE_GENERATION_STRATEGY = str(configDataNegativeTableGeneration["strategy"])
                configTenet = configData["TENET_CONFIG"]
                cls.instance.CONFIG_TENET_API_KEY = configTenet["api_key"]
                cls.instance.CONFIG_TENET_BEST_EVIDENCES = int(configTenet["bestEvidences"])
                cls.instance.CONFIG_TENET_LANGUAGE_MODEL = str(configTenet["languageModel"])
                cls.instance.CONFIG_TENET_ADDRESS = str(configTenet["address"])
                cls.instance.CONFIG_TENET_RATE_LIMIT = str(configTenet["rateLimit"]).lower == "true"
                cls.instance.CONFIG_TENET_SLEEP_TIME = int(configTenet["sleepTime"])
                cls.instance.CONFIG_TENET_NUM_THREAD = int(configTenet["num_thread"])
                configSentenceGeneration = configData["SENTENCE_GENERATION"]
                cls.instance.SENTENCE_GENERATION_OPERATIONS = configSentenceGeneration["operations"]
                cls.instance.SENTENCE_GENERATION_COMPARISONS = configSentenceGeneration["comparisons"]
            else:
                log.info("Config file not found. Use default configuration")
                path = Path(current_working_directory)
                pathCache = str(path.parent.parent.absolute()) + os.path.sep + "data"
                cls.instance.CACHE_DIR = pathCache
                cls.instance.SEED = 17
                cls.instance.NEGATIVE_TABLE_GENERATION_ADD_ROWS = True
                cls.instance.NEGATIVE_TABLE_GENERATION_ROWS_TO_ADD = 3
                cls.instance.NEGATIVE_TABLE_GENERATION_REMOVE_ROWS = False
                cls.instance.NEGATIVE_TABLE_GENERATION_ROWS_TO_REMOVE = 1
                cls.instance.NEGATIVE_TABLE_GENERATION_USE_LM = False
                cls.instance.NEGATIVE_TABLE_GENERATION_STRATEGY = Constants.STRATEGY_ACTIVE_DOMAIN
                cls.instance.CONFIG_TENET_API_KEY = "API_KEY"
                cls.instance.CONFIG_TENET_BEST_EVIDENCES = 5
                cls.instance.CONFIG_TENET_LANGUAGE_MODEL = Constants.LANGUAGE_MODEL_MISTRAL_OLLAMA
                cls.instance.CONFIG_TENET_ADDRESS = "http://host.docker.internal:11434"
                cls.instance.CONFIG_TENET_RATE_LIMIT = False
                cls.instance.CONFIG_TENET_SLEEP_TIME = 0
                cls.instance.CONFIG_TENET_NUM_THREAD = 0
                cls.instance.SENTENCE_GENERATION_OPERATIONS = [Constants.OPERATION_LOOKUP,
                                                               Constants.OPERATION_COMPARISON,
                                                               Constants.OPERATION_FILTER,
                                                               Constants.OPERATION_MIN, Constants.OPERATION_MAX,
                                                               Constants.OPERATION_COUNT,
                                                               Constants.OPERATION_SUM, Constants.OPERATION_AVG]
                cls.instance.SENTENCE_GENERATION_COMPARISONS = [Constants.OPERATOR_SAME, Constants.OPERATOR_LT,
                                                                Constants.OPERATOR_GT]
        return cls.instance
