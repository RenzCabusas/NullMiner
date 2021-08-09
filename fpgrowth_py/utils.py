from csv import reader
from collections import defaultdict

class Node:
    def __init__(self, itemName, frequency, parentNode):
        self.itemName = itemName
        self.count = frequency
        self.parent = parentNode
        self.children = {}
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

# Return the category value for the item. Item in format of "{category,item}""
def getCategoryNumber(item):
    return item.split(',')[0][1:]

# Return the name value for the item. Item in format of "{category,item}"
def getItemName(item):
    return item.split(',')[1][:-1]

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

def getNullEntryForCategory(category):
    return "{" + category + ",NULL}"

def generateTables(itemSetList, frequency, minSup, isNullEntriesIncluded):
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
            
            if headerTable[item] + nullTable[categoryNumber] < minSup:
                continue
            
            # if item's category number has null entries, merge them 
            if nullTable[categoryNumber]:
                newFrequency = headerTable[item] + nullTable[categoryNumber] # add frequencies of item and null entry
                newItem = addNullToItemName(item)
                nullEntriesToAdd[newItem] = newFrequency
        
        # merge nullEntries with headerTable
        headerTable = headerTable | nullEntriesToAdd
    return headerTable, categorySetCounts

def cleanAndSortItemSet(itemSet, headerTable, nullTable, isNullEntriesIncluded):
    newItemSet = []
    
    for item in itemSet:        
        if item in headerTable:
            newItemSet.append(item)
            continue
            
        itemNameWithNull = addNullToItemName(item)
        if itemNameWithNull in headerTable:
            newItemSet.append(itemNameWithNull)
            
    if isNullEntriesIncluded:
        newItemSet.sort(key=lambda item: nullTable[getCategoryNumber(item)], reverse=False)
    else:
        newItemSet.sort(key=lambda item: headerTable[item][0], reverse=True)
    
    return newItemSet
    
def constructTree(itemSetList, minSup, frequency, isNullEntriesIncluded):
    # headerTable: {categoryNumber, itemName}: frequency
    headerTable, categorySetCounts = generateTables(itemSetList, frequency, minSup, isNullEntriesIncluded)

    # Deleting items below minSup
    nullTable = generateNullTable(itemSetList)
    headerTable = dict((item, sup) for item, sup in headerTable.items() if nullTable[getCategoryNumber(item)] + sup >= minSup or isNullEntriesIncluded and getItemName(item) == "NULL")

    if(len(headerTable) == 0):
        return None, None

    # headerTable: {categoryNumber, itemName}: [frequency, headNode, setCount]
    for item in headerTable:
        headerTable[item] = [headerTable[item], None, nullTable[getCategoryNumber(item)]]
    
    # Init Null head node
    fpTree = Node('Null', 1, None)

    # Update FP tree for each cleaned and sorted itemSet
    for idx, itemSet in enumerate(itemSetList):
        itemSet = cleanAndSortItemSet(itemSet, headerTable, nullTable, isNullEntriesIncluded)
        # Traverse from root to leaf, update tree with given item
        currentNode = fpTree
        for item in itemSet:
            currentNode = updateTree(item, currentNode, headerTable, frequency[idx])
            
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
        
def updateTree(item, treeNode, headerTable, frequency):
    if item in treeNode.children:
        # If the item already exists, increment the count
        treeNode.children[item].increment()
    else:
        # Create a new branch
        newItemNode = Node(item, frequency, treeNode)
        treeNode.children[item] = newItemNode
        # Link the new branch to header table
        updateHeaderTable(item, newItemNode, headerTable)
     
    return treeNode.children[item]

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
    sortedItemList = [item[0] for item in sorted(list(headerTable.items()), key=lambda p:(p[1][2], p[0]), reverse=True)] 
    
    # Start with the lowest frequency
    for item in sortedItemList:
        # Pattern growth is achieved by the concatenation of suffix pattern with frequent patterns generated from conditional FP-tree
        newFreqSet = preFix.copy()
        newFreqSet.add(item)
        if newFreqSet not in freqItemList:
            freqItemList.append(newFreqSet)
            
        # Find all prefix path, constrcut conditional pattern base
        conditionalPattBase, frequency = findPrefixPath(item, headerTable) 

        # Construct conditonal FP Tree with conditional pattern base
        conditionalTree, newHeaderTable = constructTree(conditionalPattBase, minSup, frequency, isNullEntriesIncluded) 

        if newHeaderTable != None:
            # Mining recursively on the tree
            mineTree(newHeaderTable, minSup,
                       newFreqSet, freqItemList, isNullEntriesIncluded)
            
def mineTreeWithNull(headerTable, minSup, preFix, freqItemList, isNullEntriesIncluded):
    sortedItemList = [item[0] for item in sorted(list(headerTable.items()), key=lambda p:(p[1][2], p[0]), reverse=True) if getItemName(item[0]) != "NULL" and "NULL" in item[0]] 
    for item in sortedItemList:
        # Pattern growth is achieved by the concatenation of suffix pattern with frequent patterns generated from conditional FP-tree
        newFreqSet = preFix.copy()
        newFreqSet.add(item)
        if newFreqSet not in freqItemList:
            freqItemList.append(newFreqSet)

        # Find all prefix path, constrcut conditional pattern base
        conditionalPattBase, frequency = findPrefixPath(removeNullFromItemName(item), headerTable) 
        
        # get conditional path for its null entry
        nullEntry = getNullEntryForCategory(getCategoryNumber(item))
        conditionalPattBaseWithNull, frequencyWithNull = findPrefixPath(nullEntry, headerTable) 
        
        # merge conditional pattern base and frequencies
        mergedConditionalPattBase = conditionalPattBase + conditionalPattBaseWithNull
        mergedFrequencies = frequency + frequencyWithNull

        # Construct conditonal FP Tree with conditional pattern base
        conditionalTree, newHeaderTable = constructTree(mergedConditionalPattBase, minSup, mergedFrequencies, isNullEntriesIncluded) 

        if newHeaderTable != None:
            mineTreeWithNull(newHeaderTable, minSup,
                       newFreqSet, freqItemList, isNullEntriesIncluded)
            # Mining recursively on the tree
            mineTree(newHeaderTable, minSup,
                       newFreqSet, freqItemList, isNullEntriesIncluded)
                
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