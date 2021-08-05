from csv import reader
from collections import defaultdict

class Node:
    def __init__(self, itemName, frequency, parentNode):
        self.itemName = itemName
        self.count = frequency
        self.parent = parentNode
        self.children = {}
        self.nullChildren = {}
        self.next = None

    def increment(self):
        self.count += 1
    
    def printTree(self):
        print(self.numNodes())
        self.display()

    def display(self, ind=1):
        print('  ' * ind, self.itemName, ' ', self.count)
        for child in list(self.children.values()):
            child.display(ind+1)

    def numNodes(self):
        return "Number of Nodes: " + str(self.numNodesHelper() - 1)
    
    def numNodesHelper(self):
        count = 1
        for child in list(self.children.values()):
            count += child.numNodesHelper()
        return count

def getCategoryNumber(item):
    return item[1:2]

def getItemName(item):
    return item[3:-1]

def getFrequencyFromList(itemSetList):
    frequency = [1 for i in range(len(itemSetList))]
    return frequency

def generateNullTable(itemSetList):
    nullTable = defaultdict(int)
    for idx, itemSet in enumerate(itemSetList):
        for item in itemSet:
            if getItemName(item) == 'NULL':
                nullTable[getCategoryNumber(item)] += 1
    return nullTable

def addNullToItemName(item):
    newItemName = getItemName(item) + " + NULL"
    return "{" + str(getCategoryNumber(item)) + "," + str(newItemName) + "}"

def removeNullFromItemName(item):
    newItemName = getItemName(item).split(" +")[0]
    return "{" + str(getCategoryNumber(item)) + "," + str(newItemName) + "}"
        
def generateTables(itemSetList, frequency, isNullEntriesIncluded):
    headerTable = defaultdict(int)
    categorySetCounts = defaultdict(set)
    
    for idx, itemSet in enumerate(itemSetList):
        for item in itemSet:
            # get frequencies for each item in itemset
            headerTable[item] += frequency[idx]
            
            # count number of unique items for each category
            categoryNumber = getCategoryNumber(item)
            categorySetCounts[categoryNumber].add(item)
    
    if isNullEntriesIncluded:
        nullTable = generateNullTable(itemSetList)
        nullEntriesToAdd = defaultdict(int)
        
        for item in headerTable:
            categoryNumber = getCategoryNumber(item)
            itemName = getItemName(item)
            
            # skip null items
            if itemName == "NULL":
                continue
            
            # if item's category number has null entries, merge them 
            if nullTable[categoryNumber]:
                newFrequency = headerTable[item] + nullTable[categoryNumber] # add frequencies of item and null entry
                newItem = addNullToItemName(item)
                nullEntriesToAdd[newItem] = newFrequency
        
        # merge nullEntries with headerTable
        headerTable = headerTable | nullEntriesToAdd
    return headerTable, categorySetCounts

def cleanAndSortItemSet(itemSet, headerTable, isNullEntriesIncluded):
    newItemSet = []
    
    for item in itemSet:        
        if item in headerTable:
            newItemSet.append(item)
            continue
            
        itemNameWithNull = addNullToItemName(item)
        if itemNameWithNull in headerTable:
            newItemSet.append(itemNameWithNull)
            
    if isNullEntriesIncluded:
        newItemSet.sort(key=lambda item: headerTable[item][2], reverse=False)
    else:
        newItemSet.sort(key=lambda item: headerTable[item][0], reverse=True)
    
    return newItemSet
    
def constructTree(itemSetList, minSup, frequency, isNullEntriesIncluded):
    # headerTable: {categoryNumber, itemName}: frequency
    headerTable, categorySetCounts = generateTables(itemSetList, frequency, isNullEntriesIncluded)
    
    # Deleting items below minSup
    headerTable = dict((item, sup) for item, sup in headerTable.items() if sup >= minSup)
    
    if(len(headerTable) == 0):
        return None, None

    # headerTable: {categoryNumber, itemName}: [frequency, headNode, setCount]
    for item in headerTable:
        headerTable[item] = [headerTable[item], None, len(categorySetCounts[getCategoryNumber(item)])]
    
    # Init Null head node
    fpTree = Node('Null', 1, None)

    # Update FP tree for each cleaned and sorted itemSet
    for idx, itemSet in enumerate(itemSetList):
        itemSet = cleanAndSortItemSet(itemSet, headerTable, isNullEntriesIncluded)
        # Traverse from root to leaf, update tree with given item
        currentNode = fpTree
        for item in itemSet:
            currentNode = updateTree(item, currentNode, headerTable)

    return fpTree, headerTable

def updateHeaderTable(item, targetNode, headerTable):
    if(headerTable[item][1] == None):
        headerTable[item][1] = targetNode
    else:
        currentNode = headerTable[item][1]
        # Traverse to the last node then link it to the target
        while currentNode.next != None:
            currentNode = currentNode.next
        currentNode.next = targetNode
        
def updateTree(item, treeNode, headerTable):
    if item in treeNode.children:
        # If the item already exists, increment the count
        treeNode.children[item].increment()
    else:
        # Create a new branch
        newItemNode = Node(item, 1, treeNode)
        treeNode.children[item] = newItemNode
        # Link the new branch to header table
        updateHeaderTable(item, newItemNode, headerTable)
     
    return treeNode.children[item]

def addNullNodes(headerTable, itemSetList):
    nullTable = generateNullTable(itemSetList)
    for item in headerTable:
        categoryNumber = item[1:2]
        itemName = item[3:-1]
        if itemName == "NULL" or not nullTable[categoryNumber]:
            continue
        node = headerTable[item][1]
        nullPair = "{" + categoryNumber + ",NULL}"
        nullNode = headerTable[nullPair][1]
        
        while node.next != None:
            node = node.next
        node.next = nullNode
        headerTable[item][0] += headerTable[nullPair][0]

def ascendFPtree(node, prefixPath):
    if node.parent != None:
        prefixPath.append(node.itemName)
        ascendFPtree(node.parent, prefixPath)

def findPrefixPath(basePat, headerTable):
    # First node in linked list
    treeNode = headerTable[basePat][1] 
    condPats = []
    frequency = []
    while treeNode != None:
        prefixPath = []
        # From leaf node all the way to root
        ascendFPtree(treeNode, prefixPath)  
        if len(prefixPath) > 1:
            # Storing the prefix path and it's corresponding count
            condPats.append(prefixPath[1:])
            frequency.append(treeNode.count)
        # Go to next node
        treeNode = treeNode.next 
    return condPats, frequency

def mineTree(headerTable, minSup, preFix, freqItemList, isNullEntriesIncluded):
    # Sort the items with frequency and create a list
    sortedItemList = [item[0] for item in sorted(list(headerTable.items()), key=lambda p:p[1][2], reverse=True)] 

    # Start with the lowest frequency
    for item in sortedItemList:
        # Pattern growth is achieved by the concatenation of suffix pattern with frequent patterns generated from conditional FP-tree
        newFreqSet = preFix.copy()
        newFreqSet.add(item)
        freqItemList.append(newFreqSet)
        # Find all prefix path, constrcut conditional pattern base
        conditionalPattBase, frequency = findPrefixPath(item, headerTable) 

        # Construct conditonal FP Tree with conditional pattern base
        conditionalTree, newHeaderTable = constructTree(conditionalPattBase, minSup, frequency, isNullEntriesIncluded) 
        if newHeaderTable != None:
            # Mining recursively on the tree
            mineTree(newHeaderTable, minSup,
                       newFreqSet, freqItemList, isNullEntriesIncluded)
    
def mineNullTree(headerTable, minSup, preFix, freqItemList, itemSetList):
    nullTable = generateNullTable(itemSetList)
    sortedItemList = [item[0] for item in sorted(list(headerTable.items()), key=lambda p:p[1][2], reverse=True)]
    for item in sortedItemList:
        categoryNumber = item[1:2]
        itemName = item[3:-1]
        if (not nullTable[categoryNumber] or itemName == "NULL"):
            continue
        newFreqSet = preFix.copy()
        newFreqSet.add(item)
        freqItemList.append(str(newFreqSet))
        conditionalPattBase, frequency = findPrefixPath(item, headerTable) 
        nullItem = "{" + categoryNumber + ",NULL}"
        nullConditionalPattBase, nullFrequency = findPrefixPath(nullItem, headerTable) 
        mergedConditionalPattBase = conditionalPattBase + nullConditionalPattBase
        mergedFrequency = frequency + nullFrequency
        conditionalTree, newHeaderTable = constructTree(mergedConditionalPattBase, mergedFrequency, minSup) 

def mineTreeHelper(headerTable, minSup, preFix, freqItemList, itemSetList):
    # Sort the items with frequency and create a list
    sortedItemList = [item[0] for item in sorted(list(headerTable.items()), key=lambda p:p[1][2], reverse=True)] 
    # Start with the lowest frequency
    for item in sortedItemList:
        if item[3:-1] == "NULL":
            continue  
        # Pattern growth is achieved by the concatenation of suffix pattern with frequent patterns generated from conditional FP-tree
        newFreqSet = preFix.copy()
        newFreqSet.add(item)
        freqItemList.append(newFreqSet)
        # Find all prefix path, constrcut conditional pattern base
        conditionalPattBase, frequency = findPrefixPath(item, headerTable) 
        # Construct conditonal FP Tree with conditional pattern base
        conditionalTree, newHeaderTable = constructTree(conditionalPattBase, frequency, minSup) 
        if newHeaderTable != None:
            # Mining recursively on the tree
            mineTreeHelper(newHeaderTable, minSup,
                       newFreqSet, freqItemList, itemSetList)
            
def mineNullTree(headerTable, minSup, preFix, freqItemList, itemSetList):
    nullTable = generateNullTable(itemSetList)
    # Sort the items with frequency and create a list
    sortedItemList = [item[0] for item in sorted(list(headerTable.items()), key=lambda p:p[1][2], reverse=True)] 

    # Start with the lowest frequency
    for item in sortedItemList:
        if not nullTable[item[1:2]] or item[3:-1] == "NULL":
            continue  
        
        # Pattern growth is achieved by the concatenation of suffix pattern with frequent patterns generated from conditional FP-tree
        newFreqSet = preFix.copy()
        newFreqSet.add(item)
        freqItemList.append(str(newFreqSet))
        # Find all prefix path, constrcut conditional pattern base
        conditionalPattBase, frequency = findPrefixPath(item, headerTable) 
        conditionalTree, newHeaderTable = constructTree(conditionalPattBase, frequency, minSup)
        addNullNodes(newHeaderTable, itemSetList)
        if newHeaderTable != None:
            # Mining recursively on the tree
            mineTreeHelper(newHeaderTable, minSup,
                       newFreqSet, freqItemList, itemSetList)
    

def getSupport(testSet, itemSetList):
    count = 0

    for itemSet in itemSetList:
        newTestSet = set()
        newTestSetReplacedWithNull = set()
        for item in testSet:
            if "NULL" in getItemName(item):
                newTestSet.add(removeNullFromItemName(item))
                
                # count null item
                nullItemSet = "{" + getCategoryNumber(item) + ",NULL}"
                newTestSetReplacedWithNull.add(nullItemSet)
            else:
                newTestSet.add(item)
                newTestSetReplacedWithNull.add(item)

        if(newTestSet.issubset(itemSet) or newTestSetReplacedWithNull.issubset(itemSet)):
            count += 1
    return count