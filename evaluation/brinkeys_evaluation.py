import os
import sys
import csv

goldstandard = csv.reader(open('identifiers_and_brinkeys_gold_standard.csv'),delimiter=';')

goldDict = {}
for row in goldstandard:
	# fix missing leading zeroes (ugly, needs putting in a loop)
	if len(row[1]) == 8:
		row[1] = '0'+row[1]
	if len(row[2]) == 8:
		row[2] = '0'+row[2]
	if len(row[3]) == 8:
		row[3] = '0'+row[3]
	if len(row[4]) == 8:
		row[4] = '0'+row[4]
	if len(row[5]) == 8:
		row[5] = '0'+row[5]
	goldDict[row[0]] = [row[1],row[2],row[3],row[4],row[5]]
	

resultsLocation = sys.argv[1]
results = csv.reader(open(resultsLocation),delimiter=';')

precisions = []
recalls = []

for row in results:
    # get corresponding row from gold standard
    goldBrinkeys = goldDict[row[0]]
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

overallRecall = sum(recalls)/len(recalls)    
overallPrecision = sum(precisions)/len(precisions) 
f1 = 2 * ((overallPrecision * overallRecall) / (overallPrecision + overallRecall))

print(f'Precision at 3: {overallPrecision}')
print(f'Recall at 20  : {overallRecall}')
print(f'F1            : {f1}')



