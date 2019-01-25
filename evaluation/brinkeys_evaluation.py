import os
import sys
import csv
from collections import defaultdict

goldstandard = csv.reader(open('ppn_identifier_brinkies_gold.csv'),delimiter=';')

goldDict = {}
for row in goldstandard:
    # fix missing leading zeroes
    if len(row[2]) == 8:
        row[2] = '0'+row[2]
    if len(row[3]) == 8:
        row[3] = '0'+row[3]
    if len(row[4]) == 8:
        row[4] = '0'+row[4]
    if len(row[5]) == 8:
        row[5] = '0'+row[5]
    if len(row[6]) == 8:
        row[6] = '0'+row[6]

    type_ppn = sys.argv[2] # ppn
    
    if type_ppn == 'ppn':
        goldDict[row[1].lower()] = [row[2],row[3],row[4],row[5],row[6]]
    else:
        if row[0]:
            goldDict[row[0]] =  [row[2],row[3],row[4],row[5],row[6]]
            
    
resultsLocation = sys.argv[1]
results = csv.reader(open(resultsLocation),delimiter=';')

precisions = []
recalls = []
scores_per_label = defaultdict(lambda: defaultdict(lambda: 0))


for row in results:
    # get corresponding row from gold standard
    if row[0] in goldDict.keys():
        goldBrinkeys = goldDict[row[0].lower()]
        identifier = row.pop(0) # remove identifier from row
        
        # remove empty elements
        rowBrinkeys = list(filter(None, row))
        goldBrinkeys = list(filter(None, goldBrinkeys))
        

        # calculate recall at 20
        correctBrinkeys = list(set(goldBrinkeys) & set(row)) # get intersection of two lists of Brinkeys
        rowRecall = len(correctBrinkeys) / len(goldBrinkeys) # recall |correct| / |all relevant|
        #print(f'Recall: {rowRecall}')

        # calculate precision at 3
        rowFirstThree = rowBrinkeys[0:len(goldBrinkeys)] # do len of brinkeys and not 3 for when there's less than 3 brinkeys in gold
        goldFirstThree = goldBrinkeys[0:len(goldBrinkeys)]

        for brinkey in goldBrinkeys:
            scores_per_label[brinkey]['occur']+= 1
            scores_per_label[brinkey]['truePos@3']+= int(brinkey in rowFirstThree)
            scores_per_label[brinkey]['truePos@20']+= int(brinkey in rowBrinkeys)
            scores_per_label[brinkey]['falseNeg@20']+= int(brinkey not in rowBrinkeys)
        for brinkey in rowBrinkeys:
            scores_per_label[brinkey]['falsePos@3']+= int(brinkey not in goldBrinkeys)

        #print(f'row : {rowFirstThree}')
        #print(f'gold: {goldFirstThree}')
        
        correctBrinkeys = list(set(goldFirstThree) & set(rowFirstThree)) # get intersection of two lists of Brinkeys
        if len(rowFirstThree) == 0:
            rowPrecision = 0
        else:
            rowPrecision = len(correctBrinkeys) / len(rowFirstThree) # precision: |correct| / |all results|
        #print(f'Precision: {rowPrecision}')
        
        recalls.append(rowRecall)
        precisions.append(rowPrecision)
        
        #print('-----------')
    else:
        print(f'Key "{row[0]}" not found in gold standard')

overallRecall = sum(recalls)/len(recalls)
overallPrecision = sum(precisions)/len(precisions)
f1 = 2 * ((overallPrecision * overallRecall) / (overallPrecision + overallRecall))

print(f'Precision at 3: {overallPrecision}')
print(f'Recall at 20  : {overallRecall}')
print(f'F1            : {f1}')

for label, metrics in scores_per_label.items():
    if metrics['occur']<1: continue  #undefined
    if metrics['occur']<10: continue # only measure meaningfull labels
    for k,v in metrics.items():
       print(k,v)

    try:
       precision  = metrics['truePos@3']  / (metrics['truePos@3'] + metrics['falsePos@3'])
    except:
       precision = 0
    print( metrics['truePos@20'], metrics['truePos@20'] , metrics['falseNeg@20'] )

    recall  = metrics['truePos@20'] / ( metrics['truePos@20'] + metrics['falseNeg@20'] )
    print('\t'+label+' ('+str(metrics['occur'])+'x) - Precision: '+str(precision)+', recall: '+str(recall))


