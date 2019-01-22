import pandas as pd
from collections import defaultdict


pf = '_sample'

# row: Pandas series with gold standard data for one item
# meta: oai metadata (can be a subset belonging to a university)
def link_deeper(row, meta):
     identifier = ''
     # find unique row in meta that is a match
     # match by author and/ or title

     return identifier




ggc = pd.read_excel('ggc_proefschriften_v4.xlsx',dtype=object)
ggc = pd.read_csv('meta_gold.csv',delimiter = ';', dtype=object)


kmcs = defaultdict(str)         # mapping from kmc values to universities
kmcs.update({kmc: 'rug'  for kmc in ggc.kmc_4209.unique() if 'groningen' in str(kmc).lower()})
kmcs.update({kmc: 'ul'  for kmc in ggc.kmc_4209.unique() if 'leiden' in str(kmc).lower()})
kmcs.update({kmc: 'wur'  for kmc in ggc.kmc_4209.unique() if 'wageningen' in str(kmc).lower()})
kmcs.update({kmc: 'uu'  for kmc in ggc.kmc_4209.unique() if 'utrecht' in str(kmc).lower()})
kmcs.update({kmc: 'eur'  for kmc in ggc.kmc_4209.unique() if 'rotterdam' in str(kmc).lower() or 'erasmus' in str(kmc).lower()})
kmcs.update({kmc: 'tud'  for kmc in ggc.kmc_4209.unique() if 'delft' in str(kmc).lower()})

ggc['university'] = ggc.apply(lambda row: kmcs[row.kmc_4209], axis = 1)

locs = defaultdict(str)
locs.update({'utrecht':'uu','leiden':'ul','rotterdam':'eur','delft':'tud','wageningen':'wur','groningen':'rug'})

ggc.loc[ggc.kmc_4209.isna(), 'university'] = ggc.loc[ggc.kmc_4209.isna()].apply(lambda row: locs[row.plaats.strip().lower()], axis = 1)


meta_oai = pd.read_csv('meta_oai'+pf+'.csv', sep=';', dtype = object)


for univ in ['eur','tud','rug','ul','uu','wur']:
    meta = meta_oai.loc[meta_oai.university== univ]
    for row in ggc.loc[ggc.university==univ].itertuples():
        # try to match isbn
        #for col in ['isbn_10','isbn_13','isbnextra_10','isbnextra_13']:
        #    meta.loc['isbn_'+str(n)]

        # if not a unique match:
        identifier = link_deeper(row, meta)


match =  ggc.loc[(ggc['isbn_'+pf]==value) | (ggc['isbnextra_'+pf] == value)]