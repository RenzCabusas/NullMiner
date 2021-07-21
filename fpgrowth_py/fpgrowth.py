from fpgrowth_py.utils import *
import copy

def fpgrowth(itemSetList, minSup):
    frequency = getFrequencyFromList(itemSetList)
    fpTree, headerTable = constructTree(itemSetList, frequency, minSup)
    # fpTree.printTree()
    if(fpTree == None):
        print('No frequent item set')
    else:
        freqItems = []
        # TODO: Actually implement the commented part

        # mineTree(headerTable, minSup, set(), freqItems)

        nullTable = createNullTable(itemSetList)

        for k, v in headerTable.items():
            categoryNumber = k[1:2]
            item = k[3:-1]
            tempHeaderTable = copy.deepcopy(headerTable)
            
            if (nullTable[categoryNumber] and item != "NULL" and item == "ICU"):
                pair = "{" + categoryNumber + "," + item + "}"
                tempHeaderTable[pair][0] += nullTable[categoryNumber]
                for key in list(tempHeaderTable.keys()):
                    tempItem = key[3:-1]
                    if (item == tempItem):
                        newItem = item + "+NULL"
                        newPair = "{" + categoryNumber + "," + newItem + "}"
                        newNullPair = "{" + categoryNumber + ",NULL" + "}"
                        tempHeaderTable[newPair] = tempHeaderTable[pair] 
                        del tempHeaderTable[pair]
                        del tempHeaderTable[newNullPair]
                        break
                # mineTree(tempHeaderTable, minSup, set(), freqItems)

        for i in range(len(freqItems)):
            freqItems[i] = str(freqItems[i]) + " : " + str(getSupport(freqItems[i], itemSetList)) 
        # output:
        # "{'{4,NULL}'} : 1"
        # "{'{5,NULL}', '{4,NULL}'} : 1"
        # "{'{5,NULL}'} : 1"
        # "{'{4,ICU}'} : 2"
        # "{'{2,M}'} : 3"
        # "{'{2,M}', '{1,40s}'} : 3"
        # "{'{3,MB}'} : 3"
        # "{'{1,40s}', '{3,MB}'} : 3"
        # "{'{5,comm}'} : 3"
        # "{'{5,comm}', '{1,40s}'} : 3"
        # "{'{1,40s}'} : 4"
        return freqItems
