import re

#parsing the training file.
def parseTrainingFile(inputFile, inLocationsFile, inFtypes, wordDict, posDict):
    outReadableFile = open(inputFile + '.readable', 'w')
    outVectorFile = open(inputFile + '.vector', 'w')

    locationsList = readLocationsFile(inLocationsFile)

    #Reading the full senetence first and then processing it.
    with open(inputFile) as inFile:
        sentenceLines = []
        for line in inFile:
            if len(line.strip()) == 0:
                 processSentence(sentenceLines, locationsList, inFtypes, wordDict, posDict, outReadableFile, outVectorFile, False)
                 sentenceLines = []
                 continue
            sentenceLines.append(line.strip().split())

        if len(sentenceLines) != 0:
            processSentence(sentenceLines, locationsList, inFtypes, wordDict, posDict, outReadableFile, outVectorFile, False)

    inFile.close()
    outReadableFile.close()
    outVectorFile.close()
    return [wordDict, posDict]

#Parsing the test file.
def parseTestFile(inputFile, inLocationsFile, wordDict, posDict, inFtypes):
    outReadableFile = open(inputFile + '.readable', 'w')
    outVectorFile = open(inputFile + '.vector', 'w')
    locationsList = readLocationsFile(inLocationsFile)

    # Reading the full senetence first and then processing it.
    with open(inputFile) as inFile:
        sentenceLines = []
        for line in inFile:
            if len(line.strip()) == 0:
                processSentence(sentenceLines, locationsList, inFtypes, wordDict, posDict, outReadableFile, outVectorFile, True)
                sentenceLines = []
                continue
            sentenceLines.append(line.strip().split())
        if len(sentenceLines) != 0:
            processSentence(sentenceLines, locationsList, inFtypes, wordDict, posDict, outReadableFile, outVectorFile, True)

    inFile.close()
    outReadableFile.close()
    outVectorFile.close()
    return

# For locations file.
def readLocationsFile(inLocationsFile):
    locations = []
    with open(inLocationsFile) as inFile:
        for line in inFile:
            locations.append(line.strip())
    inFile.close()
    return locations

#Processing the sentence
def processSentence(inSentence, locationList, inFileTypes, wordDict, posDict, outReadableFile, outVectorFile, useDict):
    #useDict is like a flag for processing on the test file.
    if len(inSentence) == 0:
        return

    labelDict = {}
    labelDict['O'] = 0
    labelDict['B-PER'] = 1
    labelDict['I-PER'] = 2
    labelDict['B-LOC'] = 3
    labelDict['I-LOC'] = 4
    labelDict['B-ORG'] = 5
    labelDict['I-ORG'] = 6

    wordDictLength = len(wordDict.keys())
    posDictLength = len(posDict.keys())
    inSentence.insert(0, ['n/a', 'PHIPOS', 'PHI'])
    inSentence.append(['n/a', 'OMEGAPOS', 'OMEGA'])

    for i in range(1, len(inSentence)-1):
        words = inSentence[i]
        word = words[2]
        featuresReadable = ['n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a', 'n/a']
        featuresVector = [labelDict.get(words[0])]

        #WORD will always be present.
        #Using the following offset.
        #(UNK + wordsDict) + (UNK + wordsDict + PHI) + (UNK + wordsDict + PHI) +
        #(UNKPOS + posDict) + (UNKPOS + wordsDict + PHIPOS) + (UNKPOS + wordsDict + PHIPOS) +
        # + ABBR + CAP + LOC

        featuresReadable[0] = words[2]
        offset = 1
        featuresVector.append(str(offset + wordDict.get(word, 0)) + ':' + str(1))
        if useDict == True:
            val = wordDict.get(words[2], -1)
            if val == -1:
                featuresReadable[0] = 'UNK'
        offset += (wordDictLength + 1)

        if 'wordcon' in inFileTypes:
            word1 = inSentence[i - 1][2]
            word2 = inSentence[i + 1][2]
            val1 = wordDict.get(word1, -1)
            val2 = wordDict.get(word2, -1)
            if val1 == -1:
                if word1 == 'PHI':
                    val1 = word1
                    featuresVector.append(str(offset + wordDictLength + 1) + ':' + str(1))
                else:
                    val1 = 'UNK'
                    featuresVector.append(str(offset) + ':' + str(1))
            else:
                val1 = word1
                featuresVector.append(str(offset + wordDict.get(word1, 0)) + ':' + str(1))

            if val2 == -1:
                if word2 == 'OMEGA':
                    val2 = word2
                    featuresVector.append(str(offset + 1 + wordDictLength + 1 + wordDictLength + 1) + ':' + str(1))  # Check
                else:
                    val2 = 'UNK'
                    featuresVector.append(str(offset + 1 + wordDictLength + 1) + ':' + str(1)) #Check
            else:
                val2 = word2
                featuresVector.append(str(offset + 1 + wordDictLength + 1 + wordDict.get(word2, 0)) + ':' + str(1))

            featuresReadable[1] = val1 + ' ' + val2
        offset += (wordDictLength + 1 + 1)
        offset += (wordDictLength + 1 + 1)

        if 'pos' in inFileTypes:
            if useDict == False:
                featuresReadable[2] = words[1]
                featuresVector.append(str(offset + posDict.get(words[1], 0)) + ':' + '1')
            else:
                val = posDict.get(words[1], -1)
                featuresVector.append(str(offset + posDict.get(words[1], 0)) + ':' + '1')
                if val == -1:
                    featuresReadable[2] = 'UNKPOS'
                else:
                    featuresReadable[2] = words[1]
        offset += (posDictLength + 1)

        if 'poscon' in inFileTypes:
            pos1 = inSentence[i - 1][1]
            pos2 = inSentence[i + 1][1]
            val1 = posDict.get(pos1, -1)
            val2 = posDict.get(pos2, -1)
            if val1 == -1:
                if pos1 == 'PHIPOS':
                    val1 = pos1
                    featuresVector.append(str(offset + posDictLength + 1) + ':' + '1')
                else:
                    val1 = 'UNKPOS'
                    featuresVector.append(str(offset) + ':' + '1')
            else:
                val1 = pos1
                featuresVector.append(str(offset + posDict.get(pos1, 0)) + ':' + str(1))

            if val2 == -1:
                if pos2 == 'OMEGAPOS':
                    val2 = pos2
                    featuresVector.append(str(offset + 1 + posDictLength + 1 + posDictLength + 1) + ':' + str(1))
                else:
                    val2 = 'UNKPOS'
                    featuresVector.append(str(offset + 1 + posDictLength + 1) + ':' + str(1))
            else:
                val2 = pos2
                featuresVector.append(str(offset + 1 + posDictLength + 1 + posDict.get(pos2, 0)) + ':' + str(1))

            featuresReadable[3] = val1 + ' ' + val2
        offset += (posDictLength + 1 + 1)
        offset += (posDictLength + 1 + 1)

        if 'abbr' in inFileTypes:
            featuresReadable[4] = checkAbbreviation(word)
            if featuresReadable[4].lower() == 'yes':
                featuresVector.append(str(offset) + ':' + '1')
        offset += 1

        if 'cap' in inFileTypes:
            if word[0].isupper():
                featuresReadable[5] = 'yes'
                featuresVector.append(str(offset) + ':' + '1')
            else:
                featuresReadable[5] = 'no'
        offset += 1

        if 'location' in inFileTypes:
            if word in locationList:
                featuresReadable[6] = 'yes'
                featuresVector.append(str(offset) + ':' + '1')
            else:
                featuresReadable[6] = 'no'
        offset += 1

        writeToReadableFile(outReadableFile, featuresReadable)
        writeToVectorFile(outVectorFile, featuresVector)
    return

#Checking abbreviation with regex.
def checkAbbreviation(word):
    if len(word) <= 4 and re.match('[a-zA-Z\.]*\.$', word):
        return 'yes'
    return 'no'

#Writing the sentence to the readable file.
def writeToReadableFile(inFile, inFeature):
    inFile.write('WORD: ' + inFeature[0] + '\n')
    inFile.write('WORDCON: ' + inFeature[1] + '\n')
    inFile.write('POS: ' + inFeature[2] + '\n')
    inFile.write('POSCON: ' + inFeature[3] + '\n')
    inFile.write('ABBR: ' + inFeature[4] + '\n')
    inFile.write('CAP: ' + inFeature[5] + '\n')
    inFile.write('LOCATION: ' + inFeature[6] + '\n')
    inFile.write('\n')
    return

#Writing the vector to the readable file.
def writeToVectorFile(inFile, inFeatures):
    featureToWrite = ''
    for line in inFeatures:
        featureToWrite += str(line) + ' '
    featureToWrite = featureToWrite.strip()
    inFile.write(featureToWrite + '\n')
    return

#Creating the dictionary
def createDictionaries(inputFile):
    wordDict = {}
    posDict = {}
    with open(inputFile) as inFile:
        sentenceLines = []
        wordCounter = 1
        posCounter = 1
        for line in inFile:
            line = line.strip()
            if len(line) == 0:
                continue
            word = line.split()[2]
            pos = line.split()[1]
            if wordDict.get(word, 0) == 0:
                wordDict[word] = wordCounter
                wordCounter += 1
            if posDict.get(pos, 0) == 0:
                posDict[pos] = posCounter
                posCounter += 1
    inFile.close()
    return [wordDict, posDict]

def main(inArgs):
    if len(inArgs) < 5:
        print('Incorrect number of arguments specified.')
        return

    trainingFileName = inArgs[1]
    testFileName = inArgs[2]
    locationFileName = inArgs[3]
    ftypes = inArgs[5:len(inArgs)]
    ftypes = [x.lower() for x in ftypes]
    [wordDict, posDict] = createDictionaries(trainingFileName)
    [wordDict, posDict]  = parseTrainingFile(trainingFileName, locationFileName, ftypes, wordDict, posDict)
    parseTestFile(testFileName, locationFileName, wordDict, posDict, ftypes)
    return

if __name__ == '__main__':
    import sys
    args = sys.argv
    main(args)

