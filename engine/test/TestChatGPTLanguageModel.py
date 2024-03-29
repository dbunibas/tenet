import unittest

from src.textGeneration.ChatGPTLanguageModel import ChatGPTLanguageModel


class TestChatGPTLanguageModel(unittest.TestCase):

    def setUp(self):
        self.model = ChatGPTLanguageModel()
        self.model.rateLimit = False
        self.model.sleepTime = None
        self.model.enableGPT = True

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

Task: compute(min,KM)=12000, read(driver,KM)[min], compute(max,KM)=15600, read(driver,KM)
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
