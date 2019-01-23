import pandas as pd
from collections import defaultdict
import Levenshtein


pf = ''# '_sample'
#ggcf = '../ict_with_industry/meta_gold.csv' # local system
#oaif = '../ict_with_industry/meta_oai'+pf+'.csv' # local system

ggcf = '/data/meta_gold.csv'
oaif = '/data/meta_oai'+pf+'.csv'


# row: Pandas series with gold standard data for one item
# meta: oai metadata (can be a subset belonging to a university)
def link_deeper(row, meta):
    identifier = ''
	# find unique row in meta that is a match
	# match by author and/ or title
    possibleMatches = []
    goldAuthor = str(row.author).lower()
    for index, metaRow in meta.iterrows():
        if goldAuthor.endswith(metaRow['author_name_family']): # if last names match
			#if firstName in goldAuthor: # if first name in gold first name (abandoned for now, too much variety to match properly)
            possibleMatches.append(metaRow)

    if len(possibleMatches) > 0:
        # look at title
        if str(row.sub_title) != '':
            goldTitle = row.main_title.lower() + ' ' + row.sub_title.lower() # add subtitle if we have one
        else:
            goldTitle = row.main_title.lower()

		#print('goldtitle: '+goldTitle)
        prevSimilarityScore = 0
        mostSimilarScore = 0
        for match in possibleMatches:

            similarityScore = Levenshtein.ratio(goldTitle, match.title.lower())
            #similarityScore = 0.8
			#print(str(similarityScore) + ': '+match.title)
            if similarityScore > prevSimilarityScore:
                mostSimilarMatch = match
                mostSimilarScore = similarityScore
        if mostSimilarScore > 0.6:
            identifier = mostSimilarMatch.name
    return identifier

print('Obtaining ggc data and setting universities...')
ggc = pd.read_csv(ggcf,delimiter = ';', dtype=object)
ggc.fillna('', inplace = True)

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

ggc.loc[ggc.kmc_4209=='', 'university'] = ggc.loc[ggc.kmc_4209==''].apply(lambda row: locs[row.plaats.strip().lower()], axis = 1)

ggc['identifier'] = ''

print('Obtaining oai data...')
meta_oai = pd.read_csv(oaif, sep=';', dtype = object, index_col=0)
meta_oai.fillna('', inplace = True)
isbn_columns = [col for col in meta_oai.columns if 'isbn' in col]
meta_oai['author_name_family'] = meta_oai['author_name_family'].astype(str)  # probably not necessary
meta_oai['author_name_family'] = meta_oai.apply(lambda row: row.author_name_family.lower(), axis = 1)


for univ in ['eur','tud','rug','ul','uu','wur']:
    print('Starting on', univ)
    meta = meta_oai.loc[meta_oai.university== univ]


#    for row in ggc.loc[ggc.university==univ].head(10).itertuples():
    for row in ggc.loc[ggc.university==univ].itertuples():
        # try to match isbn
        isbns = [str(isbn) for isbn in [row.isbn_10, row.isbn_13, row.isbnextra_10, row.isbnextra_13] if len(isbn)>0 ]
        identifiers = set()
        for isbn in isbns:
            for column in isbn_columns:
                identifiers.update(list(meta.loc[meta[column]==isbn].index))
        if len(identifiers) ==1:
            identifier  = identifiers.pop() # should we check?
        else: # if not a unique match:
            if len(identifiers)>1: # more matches: look at author/ title
                identifier = link_deeper(row, meta.loc[identifiers])
            else: identifier = link_deeper(row, meta) # no isbn match: look for author/ title match
        ggc.loc[row.Index,'identifier'] = identifier

with open ('gold_linked.csv','w', encoding='utf-8') as f:
    f.write(ggc.to_csv(sep=';', encoding = 'utf-8'))
#print('Matched', len(ggc.loc[len(str(ggc.identifier))>3]), 'out of', len(ggc))

