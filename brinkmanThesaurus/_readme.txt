# Directory content
BrinKeysInTitle.csv - last minute file from Myrthe providing Dutch Brinkey titles used in thesis-set. Purpose was to use this set to feed to SPARQL query in order to retrieve english Wikidata concepts.

allYourBrinekysBelongToUs.png - just a fun image based on the infamous "All your base are belong to us" translation

brinkeys_wikiURIs_ugly.R - R file that retrieves english concepts from wikidata for every Brinkey (= Brinkman concept). Matches only first alternative provided.

brinkeys_wikiURIs_ugly.csv - The resulting csv from the equally named R file.

brinkeys_wikiURIs_ugly_noNA.csv - Same as above, but with all missing cases removed.

brinkeys_wikiURIs_ugly_noNA.csv-metadata.json - CoW file used to transpose the csv data into .ttl. Non-succesful attempt: difficult to handle existing URI's.

brinkeys_wikidata.ttl - resulting file from above .json file. Use with caution, triples are broken.

brinkmanthesaurus_with_URIs.csv - KB URI's for brinkmanthesaurus .

fetch_brinkman.py - attempt to retrieve english terms for Dutch Brinkeys. Failed attempt, because of 503 errors on API's (by Google).
