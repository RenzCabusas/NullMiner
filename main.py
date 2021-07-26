import csv
from fpgrowth_py import fpgrowth
itemSetList = [['{1,40s}', '{2,M}', '{3,MB}', '{4,ICU}', '{5,comm}'],
               ['{1,40s}', '{2,F}', '{3,MB}', '{4,nonICU}', '{5,comm}'],
               ['{1,40s}', '{2,M}', '{3,MB}', '{4,NULL}', '{5,NULL}'],
               ['{1,40s}', '{2,M}', '{3,ON}', '{4,ICU}', '{5,comm}']]

file = open("./Datasets/covid19-truncated.csv", "r")
csvData = csv.reader(file)

itemSetList = []
categories = next(csvData)
for row in csvData:
    #Modify each item and append to new list with cateogry number
    catList = []
    for index,item in enumerate(row):
        catList.append("{"+str(index)+","+str(item)+"}")
    #print(row)
    #print(catList)
    #Append modified category list to item set list
    itemSetList.append(catList)

freqItemSet = fpgrowth(itemSetList, minSup=20)

for item in freqItemSet:
    print(item)

#print(len(freqItemSet))