def parseFile(inputFile):
    labelDict = {}
    labelDict['B-PER'] = 'PERSON'
    labelDict['B-LOC'] = 'LOCATION'
    labelDict['B-ORG'] = 'ORGANIZATION'

    with open(inputFile) as inFile:
        matchedPerLines = []
        matchedLocLines = []
        matchedOrgLines = []

        newLineTag = ''
        newLine = ''
        newLineStartIndex = 0
        newLineEndIndex = 0
        counter = 0
        for line in inFile:
            if len(line.strip()) == 0:
                continue

            counter += 1
            words = line.strip().split()
            firstWord = words[0]
            secondWord = words[1]

            if firstWord.startswith('B'):
                #Storing the previous one first
                if len(newLine) != 0:
                    if newLineTag == 'B-PER':
                        matchedPerLines.append(newLine + '[' + str(newLineStartIndex) + '-' + str(newLineEndIndex) + ']')
                    elif newLineTag == 'B-LOC':
                        matchedLocLines.append(newLine + '[' + str(newLineStartIndex) + '-' + str(newLineEndIndex) + ']')
                    elif newLineTag == 'B-ORG':
                        matchedOrgLines.append(newLine + '[' + str(newLineStartIndex) + '-' + str(newLineEndIndex) + ']')
                    newLine = ''
                    newLineTag = ''
                    newLineStartIndex = 0
                    newLineEndIndex = 0
                newLine = secondWord
                newLineTag = firstWord
                newLineStartIndex = counter
                newLineEndIndex = counter
            elif firstWord.startswith('I'):
                #Checking if tags match.
                if newLineTag[2:len(newLineTag)] == firstWord[2:len(newLineTag)]:
                    newLine += ' ' + secondWord
                    newLineEndIndex = counter
                else:
                    if newLineTag == 'B-PER':
                        matchedPerLines.append(newLine + '[' + str(newLineStartIndex) + '-' + str(newLineEndIndex) + ']')
                    elif newLineTag == 'B-LOC':
                        matchedLocLines.append(newLine + '[' + str(newLineStartIndex) + '-' + str(newLineEndIndex) + ']')
                    elif newLineTag == 'B-ORG':
                        matchedOrgLines.append(newLine + '[' + str(newLineStartIndex) + '-' + str(newLineEndIndex) + ']')
                    newLine = ''
                    newLineTag = ''
                    newLineStartIndex = 0
                    newLineEndIndex = 0
            elif firstWord.startswith('O'):
                if newLineTag == 'B-PER':
                    matchedPerLines.append(newLine + '[' + str(newLineStartIndex) + '-' + str(newLineEndIndex) + ']')
                elif newLineTag == 'B-LOC':
                    matchedLocLines.append(newLine + '[' + str(newLineStartIndex) + '-' + str(newLineEndIndex) + ']')
                elif newLineTag == 'B-ORG':
                    matchedOrgLines.append(newLine + '[' + str(newLineStartIndex) + '-' + str(newLineEndIndex) + ']')
                newLine = ''
                newLineTag = ''
                newLineStartIndex = 0
                newLineEndIndex = 0
    return [matchedPerLines, matchedLocLines, matchedOrgLines]

def matchLists(inList1, inList2):
    correctLines = ''
    correct = 0
    for line1 in inList1:
        for line2 in inList2:
            if line1 == line2:
                correct += 1
                correctLines += line1 + ' | '

    if len(correctLines) == 0:
        correctLines = 'NONE'
    else:
        correctLines = correctLines[0:-3]

    precision = str(correct) + '/' + str(len(inList1))
    recall = str(correct) + '/' + str(len(inList2))
    if len(inList2) == 0:
        recall = 'n/a'
    if len(inList1) == 0:
        precision = 'n/a'

    return [precision, recall, correctLines, correct]

def printLines(precision, recall, lines, inStr, fileHandle):
    fileHandle.write('Correct ' + inStr + ' = ' + lines + '\n')
    fileHandle.write('Recall ' + inStr + ' = ' + recall+ '\n')
    fileHandle.write('Precision ' + inStr + ' = ' + precision + '\n')


def main(inArgs):
    if len(inArgs) < 3:
        print('Insufficient number of arguments.')
    [matchedPerLines1, matchedLocLines1, matchedOrgLines1] = parseFile(inArgs[1])
    [matchedPerLines2, matchedLocLines2, matchedOrgLines2] = parseFile(inArgs[2])

    [precisionLoc, recallLoc, locCorrectLines, locCorrect] = matchLists(matchedLocLines1, matchedLocLines2)
    [precisionPer, recallPer, perCorrectLines, perCorrect] = matchLists(matchedPerLines1, matchedPerLines2)
    [precisionOrg, recallOrg, orgCorrectLines, orgCorrect] = matchLists(matchedOrgLines1, matchedOrgLines2)

    outEvalFile = open('eval.txt', 'w')
    printLines(precisionPer, recallPer, perCorrectLines, 'PER', outEvalFile)
    outEvalFile.write('\n')
    printLines(precisionLoc, recallLoc, locCorrectLines, 'LOC', outEvalFile)
    outEvalFile.write('\n')
    printLines(precisionOrg, recallOrg, orgCorrectLines, 'ORG', outEvalFile)
    outEvalFile.write('\n')

    totalCorrect = locCorrect + perCorrect + orgCorrect
    outEvalFile.write('Average Recall = ' + str(totalCorrect) + '/' + str(len(matchedPerLines2) + len(matchedLocLines2) + len(matchedOrgLines2)) + '\n')
    outEvalFile.write('Average Precision = ' + str(totalCorrect) + '/' + str(len(matchedPerLines1) + len(matchedLocLines1) + len(matchedOrgLines1)))
    outEvalFile.close()
    return

if __name__ == '__main__':
    import sys
    args = sys.argv
    main(args)
