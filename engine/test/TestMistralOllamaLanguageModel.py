import unittest

from src.textGeneration.MistralOllamaLanguageModel import MistralOllamaLanguageModel
from src.textGeneration.MistralTogetherAILanguageModel import MistralTogetherAILanguageModel


class TestMistralOllamaLanguageModel(unittest.TestCase):

    def setUp(self):
        self.model = MistralOllamaLanguageModel(None)
        self.modelOnline = MistralTogetherAILanguageModel()

    def test_input(self):
        prompt = """
Table: Persons
-----------
Driver | Team | KM
-----------
Kolo | SnoopWest | 15600
Milo | SnoopWest | 14567
Aldo | ItaForMe | 12000
Nick | FraFor4 | 13000
----------

Task compare (min,max) --> read(driver,KM)[*],compare(>,compute(min,KM)=12000, compute(max,KM)=15600)
Example:
    """
        # Task count+min+max --> compute(count,*)=4, read(count,driver), compute(min,KM)=12000, read(driver,KM)[min], compute(max,KM)=15600, read(driver,KM)[max]
        # Task compare (min,max) --> read(driver,KM)[*],compare(>,compute(min,KM)=12000, compute(max,KM)=15600)
        # Task count+filter+lookup --> compute(count,*)=4, filter(> 12000,km), compute(count,km)=3, read(driver)
        # Task count+max --> compute(count,*)=4, read(count,driver), compute(max,KM)=15600, read(driver,KM)[max]
        # Task count+filter --> compute(count,*)=4, filter(> 12000,km), compute(count,km)=3
        # Task min+max --> compute(min,KM)=12000, read(driver,KM)[min], compute(max,KM)=15600, read(driver,KM)
        fullPrompt = self.model.getBasePrompt() + prompt
        texts = self.model.generateText(fullPrompt)
        for t in texts:
            print(t)

    def test_input2(self):
        prompt = """
Table: Persons
-----------
Name | Age | City
-----------
Mike | 48.4 | NY
Anne | 22.0 | SF
----------

Task: read(name,age,city)[*], compare(<,age)
Example:
"""
        fullPrompt = self.model.getBasePrompt() + prompt
        print(fullPrompt)
        # texts = self.model.generateText(fullPrompt, 2)
        # for t in texts:
        #    print(t)

    def test_input3(self):
        prompt = """
Table: People
-----------
name | age
-----------
John | 47.5
Mike | 25.1
----------

Task: filter(age)>22.0,compute(count,name)=2
Example:
"""
        fullPrompt = self.modelOnline.getBasePrompt() + prompt
        # print(fullPrompt)
        texts = self.modelOnline.generateText(fullPrompt, 1)
        for t in texts:
            print(t)
