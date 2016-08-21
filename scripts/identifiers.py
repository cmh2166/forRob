"""Just grabbing, eventually checking, identifiers."""
import rdflib
from rdflib.namespace import DC as dc
from rdflib.namespace import DCTERMS as dct
from rdflib.namespace import SKOS as skos
import re
import requests
from lxml import etree
import time
bibo = rdflib.Namespace("http://purl.org/ontology/bibo/")
# LoC SRU
LCSRU = "http://lx2.loc.gov:210/lcdb?version=1.1"
LCSRU += "&operation=searchRetrieve&startRecord=1&recordSchema=marcxml"
issn_q = "&query=bath.issn="
isbn_q = "&query=bath.isbn="
title_q = "&query=dc.title="
ns = {'zs': "http://www.loc.gov/zing/srw/",
      'marc': 'http://www.loc.gov/MARC21/slim',
      'mads': "http://www.loc.gov/mads/v2"}
# LoC SRU XML Parsing
numrec_xp = '/zs:searchRetrieveResponse/zs:numberOfRecords'
recID_xp = '/zs:searchRetrieveResponse/zs:records/zs:record/zs:recordData/'
recID_xp += 'marc:record/marc:controlfield[@tag="001"]'
title_xp = '/zs:searchRetrieveResponse/zs:records/zs:record/zs:recordData/'
title_xp += 'marc:record/marc:controlfield[@tag="001"]'
# LoC LCCN MADS Parsing
LCCN = "{0}/mads"
madsname_xp = "/mads:mads/mads:authority/mads:name/mads:namePart"
madslccn_xp = "/mads:mads/mads:identity[not(@invalid)]"


def addNewIDs(data):
    """Parse text fields for any external identifiers."""
    text_preds = [dct.title, bibo.shortTitle, skos.note]
    for pred in text_preds:
        for s, _, o in data.triples((None, pred, None)):
            obj = o.toPython().lower()
            if '.org/oclc' in obj:
                oclc_split = obj.split('worldcat.org/oclc/')[1]
                oclc = re.split("\n| ", oclc_split.replace(':', '').strip())[0]
                oclc = "http://worldcat.org/oclc/" + oclc
                if oclc:
                    data.add((s, bibo.oclcnum, rdflib.term.URIRef(oclc)))
            if 'issn' in obj and 'issner' not in obj and 'issnik' not in obj:
                issn_split = obj.lower().split('issn')[1]
                issn = re.split("\n| ", issn_split.replace(':', '').strip())[0]
                issn = issn.strip('.')
                if issn and re.search(r'\d', issn):
                    data.add((s, bibo.issn, rdflib.term.Literal(issn)))
            if 'isbn' in obj:
                isbn_split = obj.lower().split('isbn')[1]
                isbn = re.split("\n| ", isbn_split.replace(':', '').strip())[0]
                if isbn and re.search(r'\d', isbn):
                    data.add((s, bibo.isbn, rdflib.term.Literal(isbn)))
            if 'd-nb.info/' in obj:
                dnb_split = obj.split('d-nb.info/')[1]
                dnb = re.split("\n| ", dnb_split.strip())[0].split('/')[0]
                if dnb and dnb is not 'gnd':
                    dnb = "http://d-nb.info/" + dnb
                    data.add((s, bibo.identifier, rdflib.term.URIRef(dnb)))
            if 'lccn' in obj:
                lccn_split = obj.split('lccn')[1].strip()
                lccn = re.split("\n|;|:|/|\r", lccn_split.strip())[0].strip()
                lccn = lccn.replace(' ', '').replace('-', '')
                if not lccn.startswith('n'):
                    lccn = "n" + lccn
                lccn = "http://lccn.loc.gov/" + lccn
                if lccn:
                    data.add((s, bibo.lccn, rdflib.term.URIRef(lccn)))
        return(data)


def checkLCCN(graph):
    """Check LCCN identifiers to grab name, match w/title from Getty data."""
    for s, _, o in graph.triples((None, bibo.lccn, None)):
        obj = o.toPython().lower()
        if obj:
            val = obj.replace(' ', '').replace('-', '').strip()
            resp = requests.get(LCCN.format(val))
            time.sleep(3)
            root = etree.fromstring(resp.content)
            test = root.xpath(madsname_xp, namespaces=ns)
            if test != []:
                madsname = test[0].value
                madslccn = test[0].value


def main():
    """Adding URIs to graph taken of bibo:Documents in Getty."""
    data = rdflib.Graph().parse("data/data.nt", format="nt")
    newdata = addNewIDs(data)
    newdata.serialize(destination='data/data.nt', format='nt')


if __name__ == '__main__':
    main()
