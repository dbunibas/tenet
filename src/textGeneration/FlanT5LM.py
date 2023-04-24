from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class FlanT5LM:
    def __init__(self):
        #print("*** Init Flan T5 ***")
        ## useful for production
        self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-large")
        ## useful for development
        #self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
        #self.model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
        #print("*** Flan T5 initialized ***")
        self.maxLength = 30

    def predictCellValue(self, word):
        input = "Can you give me an antonym of " + word + "?"
        input_ids = self.tokenizer(input, return_tensors="pt").input_ids
        outputs = self.model.generate(input_ids, max_length=self.maxLength)
        gen_word = self.tokenizer.decode(outputs[0]).replace('<pad> ', '').replace('</s>', '')
        return gen_word

