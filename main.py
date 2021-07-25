from fpgrowth_py import fpgrowth
itemSetList = [['{1,40s}', '{2,M}', '{3,MB}', '{4,ICU}', '{5,comm}'],
               ['{1,40s}', '{2,F}', '{3,MB}', '{4,nonICU}', '{5,comm}'],
               ['{1,40s}', '{2,M}', '{3,MB}', '{4,NULL}', '{5,NULL}'],
               ['{1,40s}', '{2,M}', '{3,ON}', '{4,ICU}', '{5,comm}']]

freqItemSet = fpgrowth(itemSetList, minSup=3)

for item in freqItemSet:
    print(item)

print(len(freqItemSet))