import pandas as pd

links = pd.read_csv('gold_linked.csv', sep = ';')

pre = 'meta_gold.clean'
post = '.csv'

for kind in ['', '.train','.test']:
    gold_set = pd.read_csv(pre+kind+post, delimiter = ';', encoding='latin-1')

    merged = gold_set.merge(links[['ppn','identifier']], left_on = 'ppn', right_on='ppn')
    
    with open(pre+kind+'.linked'+post, 'w', encoding='utf-8') as f:
        f.write(merged.to_csv(sep = ';', encoding = 'utf-8', index = False))
