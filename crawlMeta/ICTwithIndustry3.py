#!/usr/bin/env python
# coding: utf-8

# In[3]:


import numpy as np
import pandas as pd
#from textblob import TextBlob
from langdetect import detect
from guess_language import guess_language

#import sys
#print(sys.version)


# In[4]:


uni = pd.read_csv("./data/source/meta_oai.csv", sep=";", dtype = "str")


# In[6]:


uni[uni['language'].isnull()]
#df[df['Col2'].isnull()]


# In[52]:


# subsetting the data for missing the language tags
uniLang = uni.loc[uni['language'].isnull(), ['title', 'language', 'university']]
uniLang


# In[8]:


#blob = TextBlob("I have a book")
#blob.translate(to="es")
#blobNL = TextBlob("Ik heb een boek")
#blobNL.detect_language()
#uniLang['blob']=uniLang['title']
uniLang.head()


# In[13]:


uniShort = uniLang[:3]
#uniShort['blob']=uniShort.apply(lambda row: TextBlob(str(row.title)).detect_language(), axis=1)
#so this now 'works' but throws a 503 error. Google doesn't cooperate very well


# In[12]:


detect("I bought a book")


# In[17]:


uniShort


# In[53]:


uniLang['title.str']=uniLang['title'].apply(str)
uniLang


# In[54]:


uniLang['guessLang']=uniLang['title.str'].apply(guess_language)
uniLang['detect']=uniLang['title.str'].apply(detect)


# In[55]:


uniLang


# In[58]:


#uniLang.groupby(['detect','guessLang']).count()


# In[59]:


uniLang.groupby(['detect']).count()


# In[60]:


uniLang.groupby(['guessLang']).count()


# In[ ]:




