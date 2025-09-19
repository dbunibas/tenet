import io
import os
import json
import together

from src import Constants
from src.api.ConfigSingleton import ConfigSingleton
from src.textGeneration.ILanguageModel import ILanguageModel
from src.textGeneration.TextUtils import remove_tabs, remove_endline, remove_multipleSpaces
import logging
import time
from together import Together

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class ExaoneTogetherAILanguageModel(ILanguageModel):

    def __init__(self):
        self.initModel()
        self.useCache = True
        #self.cacheFile = Constants.CACHE_DIR + "/cache_Llama3.json"
        self.cacheFile = str(ConfigSingleton().CACHE_DIR) + "cache_exaone.json"
        self.cache = {}
        self.sleepTime = ConfigSingleton().CONFIG_TENET_SLEEP_TIME  # seconds
        if self.useCache and os.path.isfile(self.cacheFile):
            # print("*** CACHE FILE: ", self.cacheFile)
            with open(self.cacheFile, 'r') as f:
                try:
                    listPrompts = json.load(f)
                    for item in listPrompts:
                        self.cache[item['prompt']] = item['texts']
                except:
                    logging.debug("*** Cache file empty")

    def initModel(self):
        pass

    def invokeModel(self, prompt, temperature=0.0):
        try:
            client = Together(api_key=ConfigSingleton().CONFIG_TENET_API_KEY)
            output = client.chat.completions.create(
                    model="lgai/exaone-3-5-32b-instruct",
                    messages=[
                      {
                        "role": "user",
                        "content": prompt
                      }
                    ],
                    temperature=temperature
            )
            modelOutput = output.choices[0].message.content
            return modelOutput
        except Exception as e:
            #print("Exception: " + str(e))
            return None

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
            temperature = 0.0
            if nSentences is not None:
                nToGenerate = nSentences
                temperature = 1.0
            for i in range(0, nToGenerate):
                sentence = self.cleanText(self.invokeModel(prompt, temperature=temperature))
                if sentence is not None:
                    texts.append(sentence)
                    temperature = temperature - 0.1
                    if temperature < 0: temperature = 0
                if self.sleepTime > 0:
                    time.sleep(self.sleepTime)
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
        if text is None: return None
        # logging.debug("Generated text (before cleaning): \n" + text)
        textCleaned = text.split("==========")
        return remove_multipleSpaces(remove_endline(remove_tabs(textCleaned[0]))).strip()

    def getBasePrompt(self):
        examples = []
        examples.append("""
Table: Persons
-----------
Name | Year | Country | Salary
-----------
Enzo | 35 | ITA | 10000
Paolo | 45 | SPA | 2000
----------

Task: read(name,country)[*]
Example: Enzo is from Italy and Paolo is from Spain.
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
        #prompt = "You are a helpful assistant that generate text from a given example. If you cannot complete task return 'FAILED'. \nPlease return only the sentence generated. Do not explain the task.\n"
        prompt = """I have some data in a table. I want you to express the data in a sentence.
To help you in adding semantics to the sentence, I will also add as metadata some functions that express the semantics I would like you to report in the sentence.

We have a set of sentences and the corresponding semantics are reported below:
- read(attrs)[*] --> read the values associated to the attrs list
- compare(comparator, attr) --> compare two or more rows on the attribute, is usually used in combination with read. Compare using the row order where the first row is the subject
- compute(function, attr) = value --> verbalize the function associated to the attribute where the values is value. Functions are min, max, avg, count and so on
- filter(attr) condition --> filter the rows where for the attribute attr the condition holds
- percentage(attribute, comparator) percValue --> read the percValue associated to the attribute
- ranked(position, attribute) --> read the position with respect to the attribute.

Here are some examples:"""
        prompt = prompt + "\n==========".join(examples) + "\n=========="
        prompt = prompt + "\n. Do not add any comments to the sentence. Do not add any information to the sentence that is not explicitly expressed by the given functions."
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
