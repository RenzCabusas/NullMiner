from fpgrowth_py.utils import *

def fpgrowth(itemSetList, minSup):
    frequency = getFrequencyFromList(itemSetList)
    fpTree, headerTable = constructTree(itemSetList, frequency, minSup)
    # fpTree.printTree()
    if(fpTree == None):
        print('No frequent item set')
    else:
        freqItems = []
        # TODO: Actually implement the commented part

        mineTree(headerTable, minSup, set(), freqItems)
        constructNullTree(headerTable, itemSetList)
        mineNullTree(headerTable, minSup, set(), freqItems, itemSetList)

        for i in range(len(freqItems)):
            freqItems[i] = str(freqItems[i]) + " : " + str(getSupport(freqItems[i], itemSetList))

        return freqItems
