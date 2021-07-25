from csv import reader
from collections import defaultdict

class Node:
    def __init__(self, itemName, frequency, parentNode):
        self.itemName = itemName
        self.count = frequency
        self.parent = parentNode
        self.children = {}
        self.next = None

    def increment(self, frequency):
        self.count += frequency
    
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

def getFromFile(fname):
    itemSetList = []
    frequency = []
    
    with open(fname, 'r') as file:
        csv_reader = reader(file)
        for line in csv_reader:
            line = list(filter(None, line))
            itemSetList.append(line)
            frequency.append(1)

    return itemSetList, frequency

def createNullTable(itemSetList):
    nullTable = defaultdict(int)
    for idx, itemSet in enumerate(itemSetList):
        for item in itemSet:
            if item[3:-1] == 'NULL':
                nullTable[item[1:2]] += 1
    return nullTable

def constructTree(itemSetList, frequency, minSup):
    headerTable = defaultdict(int)
    nullTable = createNullTable(itemSetList)    
    categorySetCounts = defaultdict(set)

    # Counting frequency and create header table
    for idx, itemSet in enumerate(itemSetList):
        for item in itemSet:
            headerTable[item] += frequency[idx]
            categorySetCounts[item[1:2]].add(item)

    # Deleting items below minSup
    headerTable = dict((item, sup) for item, sup in headerTable.items() if item[3:-1] == 'NULL' or sup >= minSup or nullTable[item[1:2]] + sup >= minSup)

    if(len(headerTable) == 0):
        return None, None

    # HeaderTable column [Item: [frequency, headNode, setCount]]
    for item in headerTable:
        headerTable[item] = [headerTable[item], None, len(categorySetCounts[item[1:2]])]

    # Init Null head node
    fpTree = Node('Null', 1, None)

    # Update FP tree for each cleaned and sorted itemSet
    for idx, itemSet in enumerate(itemSetList):
        itemSet = [item for item in itemSet if item in headerTable]
        itemSet.sort(key=lambda item: headerTable[item][2], reverse=False)

        # Traverse from root to leaf, update tree with given item
        currentNode = fpTree
        for item in itemSet:
            currentNode = updateTree(item, currentNode, headerTable, frequency[idx])

    return fpTree, headerTable

def constructNullTree(headerTable, itemSetList):
    nullTable = createNullTable(itemSetList)
    
    for item in headerTable:
        categoryNumber = item[1:2]
        itemName = item[3:-1]
        if not nullTable[categoryNumber] or itemName == "NULL":
            continue
        addNullNodes(item, headerTable)
        
def addNullNodes(item, headerTable):    
    tableEntry = headerTable[item]
        
    categoryNumber = item[1:2]
    pair = "{" + str(categoryNumber) + ",NULL}"
    nullItemEntry = headerTable[pair]
    
    node = tableEntry[1]
    nodeNullItem = nullItemEntry[1]
    while node.next != None:
        node = node.next
    node.next = nodeNullItem

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
        treeNode.children[item].increment(frequency)
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

def mineTree(headerTable, minSup, preFix, freqItemList):
    # Sort the items with frequency and create a list
    sortedItemList = [item[0] for item in sorted(list(headerTable.items()), key=lambda p:p[1][2], reverse=True)] 

    # Start with the lowest frequency
    for item in sortedItemList:
        if (headerTable[item][0] < minSup or item[3:-1] == "NULL"):
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
            mineTree(newHeaderTable, minSup,
                       newFreqSet, freqItemList)

def mineNullTree(headerTable, minSup, preFix, freqItemList, itemSetList):
    nullTable = createNullTable(itemSetList)
    # Sort the items with frequency and create a list
    sortedItemList = [item[0] for item in sorted(list(headerTable.items()), key=lambda p:p[1][2], reverse=True)] 

    # Start with the lowest frequency
    for item in sortedItemList:
        if not nullTable[item[1:2]] or item[3:-1] == "NULL":
            continue  
        
        # Pattern growth is achieved by the concatenation of suffix pattern with frequent patterns generated from conditional FP-tree
        newFreqSet = preFix.copy()
        newFreqSet.add(item)
        freqItemList.append(newFreqSet)
        # Find all prefix path, constrcut conditional pattern base
        conditionalPattBase, frequency = findPrefixPath(item, headerTable) 

        conditionalTree, newHeaderTable = constructTree(conditionalPattBase, frequency, minSup) 
        if newHeaderTable != None:
            conditionalTree.display()

            # Mining recursively on the tree
            mineNullTree(newHeaderTable, minSup,
                       newFreqSet, freqItemList, itemSetList)

        
def getSupport(testSet, itemSetList):
    count = 0
    for itemSet in itemSetList:
        if(set(testSet).issubset(itemSet)):
            count += 1
    return count


def getFrequencyFromList(itemSetList):
    frequency = [1 for i in range(len(itemSetList))]
    return frequency