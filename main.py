import csv
from fpgrowth_py import fpgrowth

NULL_VALUE = '99'
INPUT_FILE = './Datasets/covid19-truncated.csv'

itemSetList = [['{1,40s}', '{2,M}', '{3,MB}', '{44,ICU}', '{5,comm}'],
               ['{1,40s}', '{2,F}', '{3,MB}', '{44,nonICU}', '{5,comm}'],
               ['{1,40s}', '{2,M}', '{3,MB}', '{44,NULL}', '{5,NULL}'],
               ['{1,40s}', '{2,M}', '{3,ON}', '{44,ICU}', '{5,comm}']]

# file = open(INPUT_FILE, "r")
# csvData = csv.reader(file)

# itemSetList = []
# categories = next(csvData)

# for row in csvData:
#     #Modify each item and append to new list with cateogry identifier
#     catList = []
#     for index,item in enumerate(row):
#         if str(item) == NULL_VALUE:
#             item = 'NULL'
#         catList.append("{"+str(categories[index])+","+str(item)+"}")
#     itemSetList.append(catList)

#TODO Possibly calculate a percentage to generate minSup (total entries to list)
freqItemSet = fpgrowth(itemSetList, minSup=3, isNullEntriesIncluded=True)

for item in freqItemSet:
    print(item)

print(len(freqItemSet))
