import ast
import nltk
import gensim
from textaugment import Word2vec, Wordnet, Translate, EDA
from tqdm import tqdm
import os

from src import Utils


def createClaimObj(newClaim, originalObj):
    clonedObj = Utils.customDeepCopy(originalObj)
    clonedObj['claim'] = newClaim
    return clonedObj


def saveToOutput(f, obj):
    stringSave = str(obj)
    f.write(stringSave)
    dictLoaded = ast.literal_eval(stringSave)
    if type(dictLoaded) is not dict: print("*ERROR")
    f.write("\n")
    # f.flush()

if __name__ == '__main__':
    ### TODO: path files
    fileOutput = "./data/feverous_train_baseline_augmentation.jsonl"
    maxTables = None
    fileOutputFilter = "./data/feverous_train_baseline_augmentation_"+ str(maxTables) + ".jsonl"
    cachedFile = open(fileOutput)
    filtered = []
    ids =[]
    idsToExample = {}
    for line in cachedFile:
        example = ast.literal_eval(line)
        id = int(example["id"])
        label = example['label']
        if label == 'NOT ENOUGH INFO': continue
        if id not in ids: ids.append(id)
        if id not in idsToExample: idsToExample[id] = []
        examples = idsToExample[id]
        examples.append(example)
    cachedFile.close()
    idsFilter = ids
    if maxTables is not None: idsFilter = ids[0:maxTables]
    for id in idsFilter:
        examples = idsToExample[id]
        if len(examples) > 0: filtered += examples
    with open(fileOutputFilter, 'w') as f:
        for obj in filtered:
            saveToOutput(f, obj)
    print("File saved:", fileOutputFilter)



if __name__ == '__main__xxx':
    ## https://github.com/dsfsi/textaugment

    ## init text augmentation
    nltk.download('wordnet')
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')

    model = gensim.models.KeyedVectors.load_word2vec_format('/word2vec/GoogleNews-vectors-negative300.bin.gz', binary=True)
    # modelFastText = gensim.models.fasttext.load_facebook_model('./cc.en.300.bin.gz')
    word2VecAugmenter = Word2vec(model=model)
    # fastTextAugmenter = Word2vec(modelFastText)
    wordNetAugmenter = Wordnet()
    translateAugmenter = Translate(src="en", to="fr")
    edaAugmenter = EDA()
    ######## PRINT CONFIG
    printOutput = False
    ### FILE_IN and FILE_OUT def
    fileName = ".data/feverous_train.jsonl"
    fileOutput = ".data/feverous_train_baseline_augmentation.jsonl"
    visitedIds = set()
    writeType = 'w'
    if os.path.exists(fileOutput):
        writeType = 'a'
        cachedFile = open(fileOutput)
        for line in cachedFile:
            example = ast.literal_eval(line)
            id = int(example["id"])
            visitedIds.add(id)
        cachedFile.close()
        print("Resumed IDS:", len(visitedIds))
    f = open(fileName)
    examples = []
    examplesOut = []
    for line in f:
        example = ast.literal_eval(line)
        id = int(example["id"])
        if id not in visitedIds:
            examples.append(example)
    f.close()
    print("Examples to generate:", len(examples))
    ## TEXT GENERATION


    with open(fileOutput, writeType) as f:
        for example in tqdm(examples):
            try:
                claimOrig = example['claim']
                claimWord2Vec = createClaimObj(word2VecAugmenter.augment(claimOrig), example)
                # claimFastText = createClaimObj(fastTextAugmenter.augment(claimOrig), example)
                claimWordNet = createClaimObj(wordNetAugmenter.augment(claimOrig), example)
                claimTranslation = createClaimObj(translateAugmenter.augment(claimOrig), example)
                claimSynonym = createClaimObj(edaAugmenter.synonym_replacement(claimOrig), example)
                claimRandomDeletion = createClaimObj(edaAugmenter.random_deletion(claimOrig, p=0.2), example)
                claimSwap = createClaimObj(edaAugmenter.random_swap(claimOrig), example)
                claimRandomInsertion = createClaimObj(edaAugmenter.random_insertion(claimOrig), example)
                if printOutput:
                    print("Original Claim:", claimOrig)
                    print("Word2Vec Claim:", claimWord2Vec)
                    print("WordNet Claim:", claimWordNet)
                    print("Translation Claim:", claimTranslation)
                    print("Synonym Claim:", claimSynonym)
                    print("Random Deletion Claim:", claimRandomDeletion)
                    print("Swap Claim:", claimSwap)
                    print("Random Insertion Claim:", claimRandomInsertion)
                saveToOutput(f, claimWord2Vec)
                saveToOutput(f, claimWordNet)
                saveToOutput(f, claimTranslation)
                saveToOutput(f, claimSynonym)
                saveToOutput(f, claimRandomDeletion)
                saveToOutput(f, claimSwap)
                saveToOutput(f, claimRandomInsertion)
                f.flush()  ## save to file
            except:
                print("Error with claim: ", example['id'], ":", example['claim'])

