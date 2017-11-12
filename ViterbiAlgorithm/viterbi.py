import math
import numpy as np

#Reading the probability file.
def readProbabilityFile(inFilename):
    probFile = open(inFilename, "r", encoding="utf8")
    dict = {}
    for line in probFile:
        strings = line.split()
        tag = strings[0].lower() + ' ' + strings[1].lower()
        dict[tag] = float(strings[2])
    return dict

#Reading the Senteces file.
def readSenteces(inFilename):
    sentFile = open(inFilename, "r", encoding="utf8")
    sentences = []
    for line in sentFile:
        sentences.append(line.strip())
    return sentences


#Parsing the sentence.
def parseSentence(words, dict):
    print('')
    Tags = ['noun', 'verb', 'inf', 'prep']
    viterbiArray = [[0 for x in range(len(words))] for y in range(4)]
    backArray = [[0 for x in range(len(words))] for y in range(4)]
    forwardArray = [[0 for x in range(len(words))] for y in range(4)]

    print('FINAL VITERBI NETWORK')
    #Making the viterbi network along with forward network.
    y = 0
    for word in words:
        word = word.lower()
        x = 0
        for tag in Tags:
            prob1 = math.log2(dict.get(word + ' ' + tag, 0.0001))
            prob2 = 0
            prob1Fw = dict.get(word + ' ' + tag, 0.0001)
            prob2Fw = 0
            #Getting the max probability.
            if y == 0:
                prob2 = math.log2(dict.get(tag + ' ' + 'phi', 0.0001))
                prob2Fw = dict.get(tag + ' ' + 'phi', 0.0001)
            else:
                probx = []
                for i in range(4):
                    #Updating viterbi.
                    prevVal = viterbiArray[i][y - 1]
                    probTag = math.log2(dict.get(tag + ' ' + Tags[i], 0.0001))
                    probFinal = prevVal + probTag
                    probx.append(probFinal)

                    #Updating forward.
                    prevVal = forwardArray[i][y - 1]
                    probTag = dict.get(tag + ' ' + Tags[i], 0.0001)
                    probFinal = prevVal * probTag
                    prob2Fw += probFinal
                maxIndex = np.argmax(np.array(probx))
                prob2 = probx[maxIndex]
                backArray[x][y] = maxIndex
            viterbiArray[x][y] = prob1 + prob2
            forwardArray[x][y] = prob1Fw * prob2Fw
            print('P(' + word + '=' + tag + ')' + ' = ' + str('%.4f' % round(viterbiArray[x][y], 4)))
            x += 1
        y += 1
    print('')
    
    #Printing back pointer table.
    print('FINAL BACKPTR NETWORK')
    for i in range(1,len(words)):
        for j in range(4):
            print('BACKPTR(' + words[i] + '=' + Tags[j] + ') = ' + Tags[backArray[j][i]])

    print('')
    # Traversing back witht he maximum probability .
    tagSequence = []
    viterbiArray = np.array(viterbiArray)
    maxIndex = np.argmax(viterbiArray[:, -1])
    index = maxIndex
    tagSeqProbability = viterbiArray[index][len(words)-1]
    for i in range(len(words) - 1, -1, -1):
        tagSequence.append(words[i] + '->' + Tags[index])
        index = backArray[index][i]

    print('BEST TAG SEQUENCE HAS LOG PROBABILITY' + ' = ' + str('%.4f' % round(tagSeqProbability, 4)))
    for tag in tagSequence:
        print(tag)
    print('')

    #Printing the forward algorithm
    forwardArray = np.array(forwardArray)
    print('FORWARD ALGORITHM RESULTS')
    for i in range(len(words)):
        sumX = np.sum(forwardArray[:, i])
        for j in range(4):
            forwardArray[j][i] = forwardArray[j][i] / sumX
            print('P(' + words[i] + '=' + Tags[j] + ') = ' + str('%.4f' % round(forwardArray[j][i], 4)))


def main(argv):
    if len(argv) < 3:
        print('Arguments not specified')
        return
    probabilityFilename = argv[1]
    sentencesFilename = argv[2]

    dict = readProbabilityFile(probabilityFilename)
    sentences = readSenteces(sentencesFilename)

    for sentence in sentences:
        print('PROCESSING SENTENCE: ' + sentence)
        parseSentence(sentence.split(), dict)
        print('')
        print('')


if __name__ == '__main__':
    import sys
    main(sys.argv)
