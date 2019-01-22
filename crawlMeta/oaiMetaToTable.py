import os
import pandas as pd
from lxml import etree
import re

from difflib import SequenceMatcher





# ids = ['eur-oai-repub.eur.nl-100019',
#      'rug-oai-pure.rug.nl-publications_45f19e15-a6f1-41f4-9a0c-4881eec47be1',
#      'tud-oai-tudelft.nl-uuid-3869d074-4e3c-4738-b445-15dbdfd51cab',
#      'ul-oai-openaccess.leidenuniv.nl-1887_18810',
#      'uu-oai-dspace.library.uu.nl-1874_691',
#      'wur-oai-library.wur.nl-wurpubs_397634']



def get_language(l):
    languages = {'nl': 'nl', 'en':'en', 'en-nl':'en', 'en-en':'en', 'Dutch': 'nl', 'dut':'nl', 'eng': 'en', 'English': 'en', 'en-US': 'en'}
    lang = 'lang'  # ?!!!
    if type(l) == etree._Element:
        for k,v in l.attrib.items():
            if 'lang' in k: # sometimes xml-defined, sometimes user-defined
                            # see https://www.w3.org/International/questions/qa-when-xmllang
                try:
                    lang = languages[v]
                except:
                    print('Undefined language:',v)
    elif type(l) == str:
        if len(l) > 0:
            try:
                lang = languages[l.strip()]
            except:
                print('Undefined language:',l)
    return lang

def meta_table(base_dir, ggc = None):
    df = pd.DataFrame()
    for count, id_name in enumerate(os.listdir(base_dir)):
#    for count, id_name in enumerate(random.sample(os.listdir(base_dir),50)):

        univ = id_name.split('-')[0]
        print(id_name)

        path = os.path.join(base_dir, id_name, "metadata")
        if not os.path.isdir(path) and os.path.isfile(os.path.join(path, "oai_response.xml")):
            continue

        
       # with open(os.path.join(path, "oai_response.xml"), "rb") as data:
        try:
            xml = etree.parse(os.path.join(path, "oai_response.xml"))
        except:
            print('\tCould not parse xml, skipping this file.')
            continue
        r = xml.getroot()
        d = {'university':univ}
        ns = {'mods':'http://www.loc.gov/mods/v3'} # namespace for mods (should work for all theses(?))
        mods = r.find('.//mods:mods', ns)          # mods element contains the meta-data about the document
        try:


            # extract subject information (topics)
            subjects = mods.findall('.//mods:subject', ns)
            for subject in subjects:
                lang = get_language(subject)
                topics = subject.findall('.//mods:topic', ns)
                for i, topic in enumerate(topics):
                    d['topic_'+str(lang)+'_'+str(i)] = topic.text.strip()

            # extract title information, publishing info
            for k in ['title','subTitle','publisher','place', 'dateIssued']:
                try:
                    d[k] = mods.find('.//mods:'+k, ns).text.strip()
                except:
                    if k in ['title', 'dateIssued']:
                        print('\tNo',k,'found.')
                        

            # extract author and institute information

            for name_item in mods.findall('.//mods:name', ns):
                nt = name_item.attrib['type']


                for role_item in name_item.findall('.//mods:roleTerm', ns):
                    role = role_item.text.strip()
                    if role == 'aut' or role == 'author': # person is an/ the author
                        for e in name_item:
                            if 'namePart' in e.tag: d['author_name_'+ e.attrib['type']] = e.text.strip()
                            elif 'displayForm' in e.tag: d['author_name_display'] = e.text.strip()
                            elif 'affiliation' in e.tag: d['institute'] = e.text.strip()
                            elif 'role' in e.tag or 'identifier' in e.tag.lower(): continue # role and identifiers are dealt with elsewhere
                            else: print('What to do with person mod', e.tag, e.text.strip())
                    elif role == 'dgg' or role == '10808':
                        for e in name_item:
                            if 'namePart' in e.tag: d['institute'] = e.text.strip()
                    else:
                        print('\tRole unknown:',role, [e.text.strip() for e in name_item])

#             # save abstract to separate file
#             abstracts = mods.findall('.//mods:abstract', ns)
#             for abstract in abstracts:
#                 #lang = get_language(abstract) #NB mostly non-defined, at other times very unreliable: dont use it
#                 try:
#                     with open(os.path.join(abstract_dir, id_name+".txt"),'w',encoding='utf8') as f:
#                         f.write(abstract.text.strip())
#                     d['abstract_filed'] = True
#                 except:
#                     print('\tCould not write abtract to file')

            # extract document identifiers
            identifiers = mods.findall('.//mods:identifier', ns)
            ic = 0
            for i in identifiers:
                try:                                      # temp
                    id_type = i.attrib['type']            #
                except: continue                          #

                if id_type in ['hdl','nbn','pure']:
                    continue
                elif id_type == 'isbn':
                    ic +=1
                    d['isbn_'+str(ic)] = re.sub("[^0-9]", "", i.text)   # only numerals
                elif id_type == 'uri':
                    parts = i.text.split(':')
                    if parts[1]=='isbn':
                        ic +=1
                        d['isbn_'+str(ic)] = re.sub("[^0-9]", "", parts[2])   # only numerals
                elif id_type =='dai-nl':
                    d['dai'] = i.text  # author identifier
                else:
                    print('\tWhat to do with type', i.attrib['type'], i.text)

            # extract language information
            languages = mods.findall('.//mods:language', ns)
            if len(languages)>0:
                d['language'] = '-'.join([get_language(lang[0].text) for lang in languages])
        except:
            True
        if ggc:
            try:
                d['document_ppn'] = find_in_ggc(d, ggc)
            except:
                d['document_ppn'] = find_in_ggc(d, ggc)
                print('\tNot able to search in GGC')

        df = df.append(pd.Series(d, name=id_name))
        if count % 500 == 0:
            with open('messyTable.csv', 'w', encoding='utf-8') as f:
                f.write(df.to_csv(sep=';',encoding='utf-8'))
            print('500 more!')
    return df


def find_in_ggc(d, ggc):
    # compare ISBN, DAI, title, author, etc.
    ppn = None
    match = []
    for key, value in d.items():
        if len(match)>0: break # look no further, we've found a match!
        if 'isbn' in key:
            pf = str(len(value))
            match =  ggc.loc[(ggc['isbn_'+pf]==value) | (ggc['isbnextra_'+pf] == value)]
        if key == 'dai':
            match = ggc.loc[ggc['ppn_author']==value]
#        if key == 'title':
#            match = ggc.loc[ggc['main_title'].strip().lower()==value.strip().lower()]

    if len(match) >0:
        ppn = match.ppn.values[0]
    if len(match) > 1:
        print('Found more than one entry in ggc', id_name)
    return ppn

#pf = '_sample'
pf=''
base_dir = 'data'+pf


abstract_dir = os.path.join(base_dir, 'abstracts')
try: os.mkdir(abstract_dir) # remove try/ except?
except FileExistsError: True


#ggc = pd.read_excel('ggc_proefschriften_v4.xlsx',dtype=object)
meta_oai = meta_table(base_dir)#, ggc)

#print('Matched in GGC:', len(meta_oai.dropna(subset=['document_ppn'])), 'out of ', len(meta_oai))

columns_old = list(meta_oai.columns)
columns = ['university','title','subTitle','language','publisher','place','dateIssued']
columns.extend(sorted([col for col in columns_old if 'isbn' in col]))
#columns.append('document_ppn')
columns.extend([col for col in columns_old if col not in columns and 'topic' not in col])
columns.extend(sorted([col for col in columns_old if 'topic' in col]))
print(columns)

with open('meta_oai'+pf+'.csv','w',encoding='utf-8') as f:
    f.write(meta_oai.to_csv(sep=';',encoding='utf-8', columns = columns))

