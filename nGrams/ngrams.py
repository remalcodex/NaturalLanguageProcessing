import os.path
import math
import random

#Code for training the unigram and bigram
def trainNgram(inTrainingFileName):
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, inTrainingFileName)
    trainingFile = open(path, "r", encoding="utf8")

    #Creating nGrams.
    unigramDict = {}
    bigramDict = {}
    totalUniCount = 0.0
    for line in trainingFile:
        line = line.lower()
        line = line.strip()
        words = line.split()

        #Doing lower case and removing not words ''.
        trimmedWords = []
        counter = 0
        while counter < len(words):
            word = words[counter].lower()
            counter += 1
            trimmedWords.append(word)
        words = trimmedWords

        #Creating unigrams
        wordsUnigram = words
        counter = 0
        while counter < len(wordsUnigram):
            word = wordsUnigram[counter]
            unigramDict[word] = unigramDict.get(word, 0) + 1
            counter += 1
            totalUniCount += 1


        #Creating bigrams
        wordsBigrams = words
        wordsBigrams.insert(0, 'phi')
        #wordsBigrams = np.insert(wordsBigrams, 0, 'phi') # Dont ver use np command on normal lists. This command strips i from 'phi' randomaly
        counter = 0
        while counter < (len(wordsBigrams) - 1):
            bigram = wordsBigrams[counter] + " " + wordsBigrams[counter+1]
            bigramDict[bigram] = bigramDict.get(bigram, 0) + 1
            counter += 1
    return unigramDict, totalUniCount, bigramDict

#Predicting probability for unigram
def predictUnigram(inUnigramDict, inS, inTotalUniCount):
    line = inS.lower()
    line = line.strip()
    words = line.split()

    totalProb = 0
    for word in words:
        totalProb += math.log2(inUnigramDict[word] / inTotalUniCount)
    return round(totalProb, 4)

#Predicting probability for bigram
def predictBigram(inBigramDict, inS):
    line = inS.lower()
    line = line.strip()
    words = line.split()
    words.insert(0, 'phi')

    totalProb = 0
    counter = 0
    while counter < (len(words)-1):
        bigram = words[counter] + " " + words[counter+1]
        freqBigram = inBigramDict.get(bigram, 0)
        if freqBigram == 0:
            totalProb = "undefined"
            break
        else:
            prevFrequecy = 0
            for key, value in inBigramDict.items():
                keys = key.split()
                if len(keys) == 2:
                    if keys[0] == words[counter]:
                        prevFrequecy += value
            totalProb += math.log2(freqBigram/prevFrequecy)
        counter += 1

    if totalProb == "undefined":
        return totalProb
    else:
        return round(totalProb, 4)

#Predicting probability for bigram with smoothing
def predictBigramSmoothing(inBigramDict, inS, inUnigramDict):
    inUniqueWords = len(inUnigramDict)

    line = inS.lower()
    line = line.strip()
    words = line.split()
    words.insert(0, 'phi')
    totalProb = 0
    counter = 0
    while counter < (len(words) - 1):
        bigram = words[counter] + " " + words[counter + 1]
        freqBigram = inBigramDict.get(bigram, 0)
        prevFrequecy = 0
        for key, value in inBigramDict.items():
            keys = key.split()
            if len(keys) == 2:
                if keys[0] == words[counter]:
                    prevFrequecy += value
        totalProb += math.log2((freqBigram+1) / (prevFrequecy + inUniqueWords + 1))
        counter += 1
    return round(totalProb, 4)

#Predicting probability from file.
def predictFromFile(inFileName, inUnigramDict, inUniCount, inBigramDict):
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, inFileName)
    predictFile = open(path, "r", encoding="utf8")

    for line in predictFile:
        print("S = ", line.strip(), '\n')
        print("Unsmoothed Unigrams, logprob(S) = ", predictUnigram(inUnigramDict, line, inUniCount))
        print("Unsmoothed Bigrams, logprob(S) = ", predictBigram(inBigramDict, line))
        print("Smoothed Bigrams, logprob(S) = ", predictBigramSmoothing(inBigramDict, line, inUnigramDict), '\n')

#Generating language sentences
def languageGenerator(inBigramDict, inSeed, ioDepth):
    if inSeed == '.' or inSeed == '?' or inSeed == '!' or ioDepth == 0:
        return inSeed

    mainSeed = inSeed
    totalValues = 0
    inSeed = inSeed.lower()
    bigramsList = []
    for key, value in inBigramDict.items():
        keys = key.split()
        if(keys[0] == inSeed):
            bigramsList.append([key, value])
            totalValues += value

    #Taking probability of all the pairs in the bigramList
    counter = 0
    while counter < len(bigramsList):
        bigramsList[counter] = [(bigramsList[counter])[0], ((bigramsList[counter])[1]/totalValues)]
        counter += 1

    randomNumber = random.uniform(0.0, 1.0)
    startVal = 0.0
    choosenBigram = []
    for pair in bigramsList:
        maxVal = startVal + pair[1]
        if startVal <= randomNumber <= maxVal:
            choosenBigram = pair[0]
            break
        startVal = maxVal

    if not choosenBigram:
        return inSeed
    else:
        ioDepth -= 1;
        ret = mainSeed + " " + languageGenerator(inBigramDict, choosenBigram.split()[1], ioDepth)
        return ret

#Generating sentences from file
def generateLines(inFileName, inBigramDict, inDepth):
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, inFileName)
    predictFile = open(path, "r", encoding="utf8")

    for line in predictFile:
        line = line.strip()
        print("Seed = ", line, '\n')

        for i in range(10):
            print("Sentence ", (i+1), ": ", languageGenerator(inBigramDict, line, inDepth), '\n' if i == 9 else '')

def main(inArgv):
    if(len(inArgv) < 4):
        print("Less than 4 arguments in the ")
        return
    trainingFilename = inArgv[1]
    flag = inArgv[2]
    lastFileName = inArgv[3]

    unigramDict, unicount, bigramDict = trainNgram(trainingFilename)
    if flag.lower() == '-test':
        predictFromFile(lastFileName, unigramDict, unicount, bigramDict)
    elif flag.lower() == '-gen':
        generateLines(lastFileName, bigramDict, 10)

if __name__ == '__main__':
    import sys
    main(sys.argv)