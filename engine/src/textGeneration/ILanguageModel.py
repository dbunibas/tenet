class ILanguageModel:

    def generateText(self, prompt, nSentences=None) -> list:
        """Generate a textual sentence given a prompt"""
        pass

    def generatePrompt(self, evidence, commandOperation) -> str:
        """Generate the prompt given the sentence and the operation"""
        pass
