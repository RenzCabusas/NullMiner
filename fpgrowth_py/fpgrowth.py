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
        mineNullTree(headerTable, minSup, set(), freqItems, itemSetList)

        for i in range(len(freqItems)):
            freqItems[i] = str(freqItems[i]) + " : " + str(getSupport(freqItems[i], itemSetList)) 
        # output:
        # {'{4,NULL}'} : 1
        # {'{4,NULL}', '{5,NULL}'} : 1
        # {'{5,NULL}'} : 1
        # {'{4,ICU}'} : 2
        # {'{5,NULL}', '{4,ICU}'} : 0
        # {'{5,comm}', '{4,ICU}'} : 2
        # {'{1,40s}', '{5,comm}', '{4,ICU}'} : 2
        # {'{2,M}', '{5,comm}', '{4,ICU}'} : 2
        # {'{2,M}', '{1,40s}', '{5,comm}', '{4,ICU}'} : 2
        # {'{2,M}', '{4,ICU}'} : 2
        # {'{1,40s}', '{4,ICU}'} : 2
        # {'{2,M}', '{1,40s}', '{4,ICU}'} : 2
        # {'{2,M}'} : 3
        # {'{2,M}', '{1,40s}'} : 3
        # {'{3,MB}'} : 3
        # {'{1,40s}', '{3,MB}'} : 3
        # {'{5,comm}'} : 3
        # {'{3,MB}', '{5,comm}'} : 2
        # {'{2,M}', '{5,comm}'} : 2
        # {'{1,40s}', '{5,comm}'} : 3
        # {'{2,M}', '{1,40s}', '{5,comm}'} : 2
        # {'{3,MB}', '{1,40s}', '{5,comm}'} : 2
        # {'{1,40s}'} : 4
        # 23
        return freqItems
