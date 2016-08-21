"""Lookup for LC, OCLC (Works + Bibs), German National Library."""
import requests
from lxml import etree
import json
import rdflib
from rdflib.namespace import DC as dc
from rdflib.namespace import DCTERMS as dct
from rdflib.namespace import SKOS as skos
from fuzzywuzzy import fuzz
import time
bibo = rdflib.Namespace("http://purl.org/ontology/bibo/")
# LoC SRU
LCSRU = "http://lx2.loc.gov:210/lcdb?version=1.1&operation=searchRetrieve"
LCSRU += "&startRecord=1&maximumRecords=5&recordSchema=mods"
issn_q = "&query=bath.issn="
isbn_q = "&query=bath.isbn="
title_q = "&query=dc.title="
ns = {'zs': "http://www.loc.gov/zing/srw/",
      'marc': 'http://www.loc.gov/MARC21/slim',
      'mads': "http://www.loc.gov/mads/v2",
      'mods': "http://www.loc.gov/mods/v3"}
# LoC SRU XML Parsing
numrec_xp = '/zs:searchRetrieveResponse/zs:numberOfRecords'
recID_xp = '/zs:searchRetrieveResponse/zs:records/zs:record/zs:recordData/'
recID_xp += 'mods:mods/mods:identifier[@type="lccn"]'
title_xp = '/zs:searchRetrieveResponse/zs:records/zs:record/zs:recordData/'
title_xp += 'mods:mods/mods:titleInfo/mods:title'
# LoC LCCN MADS Parsing
LCCN = "https://lccn.loc.gov/{0}/mads"


def queryLCissn(graph):
    """Query LC with identifiers then title. Rank matching, store if >70."""
    # Query with ISSN
    for s, _, o in graph.triples((None, bibo.issn, None)):
        issn = o.toPython().lower()
        if issn:
            resp = requests.get(LCSRU + issn_q + issn)
            time.sleep(3)
            root = etree.fromstring(resp.content)
            num = root.xpath(numrec_xp, namespaces=ns)
            rec_title = root.xpath(title_xp, namespaces=ns)
            recID = root.xpath(recID_xp, namespaces=ns)
            if rec_title != [] and num[0] > 0:
                print(rec_title[0].text)
                print(recID[0])


def queryLCisbn(graph):
    """Query LC with identifiers then title. Rank matching, store if >70."""
    # Query with ISBN
    for s, _, o in graph.triples((None, bibo.isbn, None)):
        isbn = o.toPython().lower()
        if isbn:
            resp = requests.get(LCSRU + isbn_q + isbn)
            time.sleep(3)
            root = etree.fromstring(resp.content)
            num = root.xpath(numrec_xp, namespaces=ns)
            rec_title = root.xpath(title_xp, namespaces=ns)
            recID = root.xpath(recID_xp, namespaces=ns)
            if rec_title != [] and num[0] > 0:
                print(rec_title[0].text)
                print(recID[0])


def queryLCoclc(graph):
    """Query LC with identifiers then title. Rank matching, store if >70."""
    # Query with OCLC number


def queryLCdnb(graph):
    """Query LC with identifiers then title. Rank matching, store if >70."""
    # Query with DNB number


def queryLCtitle(graph):
    """Query LC with identifiers then title. Rank matching, store if >70."""
    for URI in graph.subjects(None, None):
        matched = False
        # Query with Short Title First because better matching possibilities
        for s, _, o in graph.triples((URI, bibo.shortTitle, None)):
            shortTitle = o.toPython().lower()
            if shortTitle:
                resp = requests.get(LCSRU + title_q + shortTitle)
                time.sleep(3)
                root = etree.fromstring(resp.content)
                num = root.xpath(numrec_xp, namespaces=ns)
                rec_title = root.xpath(title_xp, namespaces=ns)
                recID = root.xpath(recID_xp, namespaces=ns)
                if rec_title != [] and num[0] > 0:
                    score = fuzz.partial_ratio(shortTitle, rec_title[0].text)
                    print(shortTitle, rec_title[0].text)
                    print("Score: " + str(score))
                    if score > 60:
                        graph.add((s, bibo.lccn, rdflib.term.URIRef(recID)))
                        matched = True
        if not matched:
            # Query with Title
            for s, _, o in graph.triples((URI, dc.title, None)):
                title = o.toPython().lower()
                if title:
                    resp = requests.get(LCSRU + title_q + title)
                    time.sleep(3)
                    root = etree.fromstring(resp.content)
                    num = root.xpath(numrec_xp, namespaces=ns)
                    rec_title = root.xpath(title_xp, namespaces=ns)
                    recID = root.xpath(recID_xp, namespaces=ns)
                    if rec_title != [] and num[0] > 0:
                        score = fuzz.partial_ratio(title, rec_title[0].text)
                        print(title, rec_title[0].text)
                        print("Score: " + str(score))
                        if score > 60:
                            graph.add((s, bibo.lccn, rdflib.term.URIRef(recID)))
                            matched = True


def main():
    data = rdflib.Graph().parse("data/data.nt", format="nt")
    newdata = queryLCtitle(data)


if __name__ == '__main__':
    main()
