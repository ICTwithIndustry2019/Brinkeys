#!/usr/bin/env python3

import os
import json
from SPARQLWrapper import SPARQLWrapper, JSON


def load_brinkman():
    if not os.path.isfile("brinkman.json"):
        sparql = SPARQLWrapper("http://data.bibliotheken.nl/sparql")

        res = set()

        for i in range(0, 15055-10, 10):
            sparql.setQuery("""
            select ?label where {

            ?s skos:inScheme <http://data.bibliotheken.nl/id/scheme/brinkman> .
            ?s rdfs:label ?label .

            } LIMIT 10 OFFSET %s
            """ % str(i))

            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            for result in results["results"]["bindings"]:
                res.add(result["label"]["value"])

        with open("brinkman.json", "wb")  as fh:
            fh.write(bytes(json.dumps(list(res)), "UTF-8"))
    else:
        with open("brinkman.json", "rb") as fh:
            res = json.loads(fh.read().decode("UTF-8"))

    return list(res)

print("Loading brinkman..")
br = load_brinkman()
print("Loadin brinkman done, %i terms available" % len(br))
print(br[0])
print(br[-1])
