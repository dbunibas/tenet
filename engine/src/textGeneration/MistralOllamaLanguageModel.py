import io
import os
import json
from langchain_community.llms import Ollama
from src import Constants
from src.api.ConfigSingleton import ConfigSingleton
from src.textGeneration.ILanguageModel import ILanguageModel
from src.textGeneration.TextUtils import remove_tabs, remove_endline, remove_multipleSpaces
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class MistralOllamaLanguageModel(ILanguageModel):

    def __init__(self, address):
        self.model = self.initModel(address)
        self.useCache = True
        # self.cacheFile = Constants.CACHE_DIR + "cache_Mistral.json"
        self.cacheFile = str(ConfigSingleton().CACHE_DIR) + "cache_Mistral.json"
        self.cache = {}
        if self.useCache and os.path.isfile(self.cacheFile):
            # print("*** CACHE FILE: ", self.cacheFile)
            with open(self.cacheFile, 'r') as f:
                try:
                    listPrompts = json.load(f)
                    for item in listPrompts:
                        self.cache[item['prompt']] = item['texts']
                except:
                    logging.info("*** Cache file empty:")
                    # print("*** Cache file empty")

    def initModel(self, address):
        llm = None
        if address is None:
            log.debug("*** LOAD MISTRAL")
            llm = Ollama(model="mistral")
            log.debug(llm.__dict__)
        else:
            log.debug("*** LOAD MISTRAL from:" + address)
            llm = Ollama(model="mistral", base_url=address)
            log.debug(llm.__dict__)
        return llm

    def generateText(self, prompt, nSentences=None) -> list:
        ## TODO: if nSentences != None --> check Ollama temperature setting
        texts = None
        if self.useCache:
            cachedResult = self.cache.get(prompt)
            if cachedResult is not None:
                texts = cachedResult.get("text")
        if texts is None:
            texts = []
            nToGenerate = 1
            if nSentences is not None: nToGenerate = nSentences
            for i in range(0, nToGenerate):
                sentence = self.cleanText(self.model.invoke(prompt))
                texts.append(sentence)
            if self.useCache:
                result = {"text": texts}
                self.cache[prompt] = result
                toJson = []
                for key, value in self.cache.items():
                    toJson.append({"prompt": key, "texts": value})
                jsonString = json.dumps(toJson, indent=4)
                with io.open(self.cacheFile, 'w') as f:
                    f.write(jsonString)
        return texts

    def generatePrompt(self, evidence, commandOperation) -> str:
        """Generate the prompt given the sentence and the operation.
           We use the same strategy of ChatGPTLanguageModel"""
        basePrompt = self.getBasePrompt()
        linearizedData = self.linearizeEvidence(evidence)
        task = "Task: " + commandOperation + "\n"
        example = "Example: "
        return basePrompt + linearizedData + task + example

    def cleanText(self, text):
        logging.debug("Generated text (before cleaning): \n" + text)
        textCleaned = text.split("==========")
        return remove_multipleSpaces(remove_endline(remove_tabs(textCleaned[0]))).strip()

    def getBasePrompt(self):
        examples = []
        examples.append("""
Table: Persons
-----------
Name | Year
-----------
Enzo | 35
null | null
Paolo | 45
John | null
----------

Task: read(name,year)[*]
Example: Enzo is 35 and Paolo is 45 years old.
""")

        examples.append("""
Table: Persons
-----------
Name | Year | Country | Salary
-----------
Enzo | 35 | ITA | 10000
Paolo | 45 | SPA | 2000
----------

Task: read(name,year)[*]
Example: Enzo is 35 and Paolo is 45 years old.
""")

        examples.append("""
Table: Persons
-----------
Name | Year | Income
-----------
Paolo | 45 | 1500
Enzo | 35 | 1000
----------

Task: read(name,year,income)[*], compare(<,year), compare(>,income)
Example: Enzo is 35 years old and is younger than Paolo. But Paolo has an income of 1500 that is higher than the Enzo's income that is 1000.
""")

        examples.append("""
Table: Persons
-----------
Name | Surname | Year
-----------
Enzo | Rossi | 35
Paolo | Verdi | 45
----------

Task: read(name, surname)[*], compare(>,year)
Example: Paolo Verdi is older than Enzo Rossi.
""")

        examples.append("""
Table: Persons
-----------
Name | Surname | Year | City
-----------
Enzo | Rossi | 50 | PZ
Paolo | Verdi | 30 | Rome
----------

Task: read(surname,name)[*], compare(<,year)
Example: Verdi Paolo is younger than Rossi Enzo.
""")

        examples.append("""
Table: Universities
-----------
School | Faculty | Students
-----------
Roma 3 | Mathematics | 4500
Unibas | Computer Science | 3500
----------

Task: read(faculty,school,students)[*], compare(<,students)
Example: The faculty of Computer Science of Unibas has 3500 students which is less than the Faculty of Mathematics of Roma 3 that has 4500 students.
""")

        examples.append("""
Table: Persons
-----------
Name | Year
-----------
Enzo | 35
Paolo | 45
John | 35
-----------

Task: read(name,year)[year=35], compare(<,year)
Example: Enzo and John are 35 and both are younger than Paolo.
 """)
        examples.append("""
Table: Persons
-----------
Name | Year
-----------
Enzo | 25
Paolo | 25
----------

Task: read(name)[*], compare(=,year)
Example: Enzo and Paolo have the same age.
""")

        examples.append("""
Table: Persons
-----------
Name | Year
-----------
Enzo | 23
Paolo | 22
John | 35
----------

Task: compute(max,year)=35, read(name)[max]
Example: John is the oldest.
""")

        examples.append("""
Table: Persons
-----------
Name | Year
-----------
Enzo | 23
Paolo | 22
John | 35
----------

Task: compute(max,year)=35, read(name,year)[max]
Example: John is the oldest, and he's 35 years old.
""")

        examples.append("""
Table: Persons
-----------
Name | Year
-----------
Enzo | 35
Paolo | 22
John | 35
----------

Task: compute(max,year)=35, read(name,year)[max]
Example: John and Enzo are the oldest with 35 years old.
""")

        examples.append("""
Table: Persons
-----------
Name | Year
-----------
John | 22
Enzo | 35
Paolo | 22
----------

Task: compute(min,year)=22, read(name,year)[min]
Example: Paolo and John are the yougest with 22 years old.
""")

        examples.append("""
Table: Persons
-----------
Name | Year
-----------
Enzo | 36
Paolo | 46
Mike | 18
----------

Task: compute(count,*)=3, read(count,name)
Example: There are three persons. Namely Enzo, Paolo and Mike.
""")

        examples.append("""
Table: Persons
-----------
Name | Year
-----------
Enzo | 36
Paolo | 46
Mike | 18
----------

Task: compute(avg,year)=33.33, read(avg)
Example: The average age is 33.33.
""")

        examples.append("""
Table: Persons
-----------
Name | Year
-----------
Enzo | 36
Paolo | 46
Mike | 18
----------

Task: filter(> 12,age), compute(count,*)=3, read(name)
Example: There are three persons with age greater than 12. Namely Enzo, Paolo and Mike.
""")

        examples.append("""
Table: Persons
-----------
Name | Country
-----------
Enzo | ITA
Paolo | ITA
Mike | ITA
----------

Task: filter(= ITA, country), compute(count,*)=3, read(Name,Country)
Example: There are three persons from Italy. Namely Enzo, Paolo and Mike.
""")

        examples.append("""
Table: Persons
-----------
Name | Year
-----------
Gianni | 50
Enzo | 36
Paolo | 46
Mike | 18
----------

Task: ranked(2,asc,Year)=36
Example: Enzo is the 2nd youngest person
""")

        examples.append("""
Table: Persons
-----------
Name | Year
-----------
Enzo | 36
Paolo | 46
Mike | 18
Gianni | 50
----------

Task: ranked(3,desc,Year)=36
Example: Enzo is the 3rd oldest person
""")

        examples.append("""
Table: Persons
-----------
Name | Income
-----------
Paolo | 36000
Enzo | 24000
----------

Task: percentage(income, <)=-50.0%
Example: Enzo has 50% of the income lower than Paolo
""")

        examples.append("""
Table: Persons
-----------
Name | Income
-----------
Enzo | 24000
Paolo | 36000
----------

Task: read(name,income)[*] percentage(income, >)=33.33%
Example: Paolo has 33.33% of the income higher than Enzo
""")
        prompt = "You are a helpful assistant that generate text from a given example. If you cannot complete task return 'FAILED'. \nPlease return only the sentence generated. Do not explain the task.\n"
        prompt = prompt + "\n==========".join(examples) + "\n=========="
        return prompt

    def linearizeEvidence(self, evidence) -> str:
        linerizedTable = "Table: " + evidence.tableName + "\n"
        lineSeparator = "-" * 12 + "\n"
        linerizedTable += lineSeparator
        headers = evidence.headers
        headerNames = evidence.getHeaderNames()
        headerLine = " | ".join(headerNames) + "\n"
        linerizedTable += headerLine
        linerizedTable += lineSeparator
        for row in evidence.orderedRows:
            cellValues = []
            for header in headerNames:
                cell = row[header]
                value = ""
                if cell is not None:
                    value = str(cell.value)
                cellValues.append(value)
            rowLine = " | ".join(cellValues) + "\n"
            linerizedTable += rowLine
        linerizedTable += lineSeparator + "\n"  # add another endline
        return linerizedTable
