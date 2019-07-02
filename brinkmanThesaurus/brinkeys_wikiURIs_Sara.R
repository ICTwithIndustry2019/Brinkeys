# wikidata
# install.packages("WikidataR")
library(WikidataR)


# call to wikidata for topic (plus language) to yield top 1 result
URIretrieve <- function(topics) {
    res <- find_item(topics, lang = "nl", limit = 1)
    res[[1]]$url # wikidata url for the first result
}


# fakeData
df <- data.frame(Brinkey = c("http://data.bibiotheken.nl/id/thes/p075598272", 
                                "http://data.bibliotheken.nl/id/thes/p075598280",
                                "http://data.bibliotheken.nl/id/thes/p075598299"),
                    topics = c("aandelen", "aardbevingen", "aarde"),
                 stringsAsFactors = FALSE)

# URIretrieve("Harderwijk") it works

df$wikidata <- sapply(df$topics, URIretrieve)

# now for real
#df <- read.csv("./brinkmanThesaurus/brinkmanthesaurus_with_URIs.csv",
df <- read.csv("brinkmanthesaurus_with_URIs_sample.csv",
               stringsAsFactors = FALSE, header = FALSE, col.names = c("bURIs", "topics"))

# takes more than an hour to run and provides answers in list.
# please fix before running again
# df$wikiURI <- sapply(df$topics, URIretrieve)


# no match:
# - plural (computersystemen vs computersysteem)
# - addition (Spijk (G) vs Spijk, sterrenbeelden (astrologie) vs sterrenbeeld)
# - character encoding of accents (syndroom van Guillain-BarreÌ vs syndroom van Guillain-Barré)
# - different formulation (Polder Oukoop en Negenviertel vs Oukoop en Negenviertel, Griekse recepten vs Griekse keuken)
# - samenstellingen (consumentenaangelegenheden, Zweedse taalkunde)



# attempt to fix list format
ul <- function (x) {
    unlist(df$wikiURI[x])[[1]]
}

df$wiki <- sapply(1:nrow(df), ul)
df$wiki

table(df$wiki=="NULL")
df$wiki[df$wiki=="NULL"] <- NA
table(is.na(df$wiki))

df$wiki2 <- unlist(df$wiki)

# 10802 URI's gelinkt
# nog wel in lelijke list... :(
# next: retrieve language tags

df.out <- df[, c("bURIs", "topics", "wiki2")]
write.csv(df.out, "./brinkmanThesaurus/brinkeys_wikiURIs_ugly.csv", row.names = FALSE)

# remove missing values
df.out.NoNA <- df.out[!is.na(df$wiki2), ]
df.out.NoNA$bURIs <- str_sub(df.out.NoNA$bURIs, start=2, end=-2)



# remove brackets from first column
write.csv(df.out.NoNA, "./brinkmanThesaurus/brinkeys_wikiURIs_ugly_noNA.csv", row.names = FALSE)



names(df)
df$wiki[7]
df[is.na(df$wiki), ]
table(df$wiki=="NULL")

df.nolink <- df[df$wiki=="NULL", ]
table(grepl("Test", df.nolink$topics))

m <- regexpr("/^[T]est$/", df.nolink$wiki)
regmatches(df.nolink$wiki, m)

library(stringr)
table(str_detect(df.nolink$topics, "^T[E-e][S-s][T-t]."))

testbrinkeys <- df.nolink[str_detect(df.nolink$topics, "^T[Ee][Ss][Tt]."), ]


# Idea: find minimal path length between Brinkeys in the wikidata ontology
# (or more finegrained information about relation)
# in order to evaluate quality of results 

