from fpgrowth_py.utils import *

def fpgrowth(itemSetList, minSup, isNullEntriesIncluded):
    frequency = getFrequencyFromList(itemSetList)
    fpTree, headerTable = constructTree(itemSetList, minSup, frequency, isNullEntriesIncluded)

    # fpTree.display()
    if(fpTree == None):
        print('No frequent item set')
    else:
        freqItems = []
        # TODO: Actually implement the commented part
        mineTree(headerTable, minSup, set(), freqItems, isNullEntriesIncluded)
        
        if isNullEntriesIncluded:
            mineTreeWithNull(headerTable, minSup, set(), freqItems, isNullEntriesIncluded)

        actualFreqItems = []
        for item in freqItems:
            sup = getSupport(item, itemSetList)
            
            actualFreqItems.append(str(item) + " : " + str(sup))
            
        return actualFreqItems
