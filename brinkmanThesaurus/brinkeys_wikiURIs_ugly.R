# wikidata


# working directory
setwd("~/git/Brinkeys/")


# libraries
install.packages("WikidataR")
library(WikidataR)

# fakeData
df <- data.frame(Brinkey = c("http://data.bibiotheken.nl/id/thes/p075598272", 
                                "http://data.bibliotheken.nl/id/thes/p075598280",
                                "http://data.bibliotheken.nl/id/thes/p075598299"),
                    topics = c("aandelen", "aardbevingen", "aarde"),
                 stringsAsFactors = FALSE)

# test <- unlist(find_item("aardgaswinning", lang = "nl", limit = 1))[3]
# test

URIretrieve <- function(topics) {
    unlist(find_item(topics, lang = "nl", limit = 1))[3]
}

URIretrieve("Harderwijk")
lapply(df[1:3])
df[1:3,1]
sapply(df[1:3,1], nchar)
cbind(sapply(df[1:3,2], URIretrieve))

df$wikidata <- sapply(df$topics, URIretrieve)

# now for real
df <- read.csv("./brinkmanThesaurus/brinkmanthesaurus_with_URIs.csv",
               stringsAsFactors = FALSE, header = FALSE, col.names = c("bURIs", "topics"))

# takes more than an hour to run!
# df$wikiURI <- sapply(df$topics, URIretrieve)

ul <- function (x) {
    unlist(df$wikiURI[x])[[1]]
}

df$wiki <- sapply(1:nrow(df), ul)
length(unlist(df$wiki))
# 10802 URI's gelinkt
# nog wel in lelijke list... :(
# next: retrieve language tags

write.csv(df, "./brinkmanThesaurus/brinkeys_wikiURIs_ugly.csv")




