import csv
from fpgrowth_py import fpgrowth

# Set to the NULL value present in the input file (example: '99')
NULL_VALUE = 'x'
# Set to the input file
INPUT_FILE = './Datasets/covid19-truncated.csv'
# Set to desired minimum support (if percentage, set SUPPORT_PERCENTAGE = True)
SUPPORT = 20
SUPPORT_PERCENTAGE = True

itemSetList = [['{1,40s}', '{2,M}', '{3,MB}', '{44,ICU}', '{5,comm}'],
               ['{1,40s}', '{2,F}', '{3,MB}', '{44,nonICU}', '{5,comm}'],
               ['{1,40s}', '{2,M}', '{3,MB}', '{44,NULL}', '{5,NULL}'],
               ['{1,40s}', '{2,M}', '{3,ON}', '{44,ICU}', '{5,comm}']]

file = open(INPUT_FILE, "r")
csvData = csv.reader(file)

itemSetList = []

# First line of csv file contains category headers, store them in seperate variable for use later
categories = next(csvData)

# Row count for calculating support in percentage
numRows = 0

# Read in each row within the input file (csv) and parse into a list
for row in csvData:
    #Modify each item and append to new list with cateogry identifier
    catList = []
    for index,item in enumerate(row):
        if str(item) == NULL_VALUE:
            item = 'NULL'
        catList.append("{"+str(categories[index])+","+str(item)+"}")
    itemSetList.append(catList)
    numRows += 1

# Calculate a percentage to generate minSup if flag set in constant
support = SUPPORT
if SUPPORT_PERCENTAGE:
    support = round((support / 100) * numRows)

# Build and mine the trees
freqItemSet = fpgrowth(itemSetList, minSup=support, isNullEntriesIncluded=True)

# Print out each frequent itemset
for item in freqItemSet:
    print(item)

print('---END OF FREQUENT ITEMS---')
print('Number of rows input: ', numRows)
print('Minimum support used: ', support)
print('Number of frequent itemsets: ', len(freqItemSet))
