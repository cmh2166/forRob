"""Stored methods for ease of access."""
import requests
import rdflib
from rdflib.namespace import DC
RDAU = rdflib.Namespace("http://rdaregistry.info/Elements/u/")
import re
import json
from lxml import etree
from fuzzywuzzy import fuzz
import time
ns = {'zs': "http://www.loc.gov/zing/srw/",
      'marc': 'http://www.loc.gov/MARC21/slim',
      'mads': "http://www.loc.gov/mads/v2"}
# OCLC Worldcat Search API
wc_search = 'http://www.worldcat.org/webservices/catalog/content/{0}?wskey='
wc_search += 'nbWiGTgZTLTMndgEmHgXOL34v3AwNjBw69S7hLGZtH7K8lzov98fHgsFNiaFxFdmgFPVnJEu6lvTAjpm'
marctitle_xp = "//marc:datafield[@tag='020']/marc:subfield[@code='a']"
marcisbn_xp = "//marc:datafield[@tag='245']/marc:subfield[@code='a']"
# LoC LCCN MADS Parsing
LCCN = "https://lccn.loc.gov/{0}/mads"
madsname_xp = "/mads:mads/mads:authority/mads:name/mads:namePart"
madslccn_xp = "/mads:mads/mads:identity[not(@invalid)]"
# LoC SRU
LCSRU = "http://lx2.loc.gov:210/lcdb?version=1.1"
LCSRU += "&operation=searchRetrieve&startRecord=1&recordSchema=marcxml"
issn_q = "&query=bath.issn="
isbn_q = "&query=bath.isbn="
title_q = "&query=dc.title="
# LoC SRU XML Parsing
numrec_xp = '/zs:searchRetrieveResponse/zs:numberOfRecords'
recID_xp = '/zs:searchRetrieveResponse/zs:records/zs:record/zs:recordData/'
recID_xp += 'marc:record/marc:controlfield[@tag="001"]'
title_xp = '/zs:searchRetrieveResponse/zs:records/zs:record/zs:recordData/'
title_xp += 'marc:record/marc:controlfield[@tag="001"]'
# OCLC ISBN Lookup
isbnx = 'http://xisbn.worldcat.org/webservices/xid/isbn/{0}'
isbnx += '?method=getMetadata&format=json&fl=*'
oclc_re = re.compile(r"http://www.worldcat.org/oclc/[0-9]{9}")
# OCLC ISSN Lookup
issnx = 'http://xissn.worldcat.org/webservices/xid/issn/{0}'
issnx += '?method=getMetadata&format=json&fl=*'


def checkOCLCworldcat(data):
    """Worldcat Search API has test key, limited to 100 calls per day."""
    for n in data:
            for oclc in data[n]['oclc']:
                if oclc:
                    oclcid = oclc.replace('http://worldcat.org/oclc/', '')
                    url = wc_search.format(oclcid)
                    resp = requests.get(url)
                    tree = etree.fromstring(resp.content)
                    isbn = tree.xpath(marctitle_xp, namespaces=ns)
                    title = tree.xpath(marcisbn_xp, namespaces=ns)
                    for m in isbn:
                        if m.text not in data[n]['isbn']:
                            data[n]['isbn'].append(m.text)
                    for l in title:
                        title_score = fuzz.partial_ratio(data[n]['title'][0],
                                                         l.text)
                        if title_score < 80:
                            print(n)
                            print(oclc)
                            print(data[n]['title'][0])
                            print(l.text)


def matchLCCN(data):
    """Check LCCN identifiers to grab name, match w/title from Getty data."""
    for n in data:
            for lccn in data[n]['lccn']:
                if lccn:
                    val = lccn.replace(' ', '').replace('-', '').strip()
                    resp = requests.get(LCCN.format(val))
                    print(resp.content)
                    time.sleep(3)
                    root = etree.fromstring(resp.content)
                    test = root.xpath(madsname_xp, namespaces=ns)
                    if test != []:
                        madsname = test[0].value
                        madslccn = test[0].value


def titleMatch(data):
    for n in data:
        for title in (data[n]['shortTitle'] + data[n]['title'] + data[n]['note']):
            if title:
                url = LCSRU + title_q + title
                resp = requests.get(url).text
                print(resp)
            return(data)


def matchGND(data):
    for n in data:
        for dnb in data[n]['dnb']:
            if dnb:
                dnb = dnb.replace('/about/rdf', '')
                resp = requests.get(dnb + '/about/lds',
                                    headers={'Accept': 'application/turtle'})
                try:
                    grp = rdflib.Graph().parse(data=resp.content, format='turtle')
                    for o in grp.objects(rdflib.term.URIRef(dnb), DC.identifier):
                        if '(OColc)' in o and o.replace('(OColc)', '') not in data[n]['oclc']:
                            newoclc = 'http://worldcat.org/oclc/' + o.replace('(OColc)', '')
                            print(newoclc)
                            data[n]['oclc'].append(newoclc)
                    doc_title = data[n]['title'][0]
                    resp_title = ''
                    title_score = title2_score = 0
                    for o in grp.objects(rdflib.term.URIRef(dnb), DC.title):
                        title_score = fuzz.partial_ratio(doc_title, o)
                        resp_title = o
                    for o in grp.objects(rdflib.term.URIRef(dnb), RDAU.P60493):
                        title2_score = fuzz.partial_ratio(doc_title, o)
                    if max(title_score, title2_score) < 80:
                        print(doc_title)
                        print(resp_title)
                except rdflib.plugins.parsers.notation3.BadSyntax:
                    if dnb == 'http://d-nb.info/gnd/':
                        data[n]['dnb'].remove(dnb)
                    print('ERROR URI: ' + n)
            return(data)


def matchingISBN(data):
    for n in data:
        for isbn in data[n]['isbn']:
            url = isbnx.format(isbn)
            resp = requests.get(url).json()
            if 'list' in resp:
                resp_title = resp_lc = resp_oclc = ''
                doc_title = data[n]['title'][0]
                if 'title' in resp['list'][0]:
                    resp_title = resp['list'][0]['title']
                if 'lccn' in resp['list'][0]:
                    resp_lc = resp['list'][0]['lccn'][0]
                if 'oclcnum' in resp['list'][0]:
                    resp_oclc = resp['list'][0]['oclcnum'][0]
                title_score = fuzz.partial_ratio(doc_title, resp_title)
                if title_score < 80:
                    print(resp_title)
                    print(doc_title)
                    print(title_score)
                    if resp_lc not in data[n]['lccn']:
                        data[n]['lccn'].append(resp_lc)
                    if 'http://worldcat.org/oclc/' + resp_oclc not in data[n]['oclc']:
                        data[n]['oclc'].append('http://worldcat.org/oclc/' + resp_oclc)
                else:
                    if resp_lc not in data[n]['lccn']:
                        data[n]['lccn'].append(resp_lc)
                    if 'http://worldcat.org/oclc/' + resp_oclc not in data[n]['oclc']:
                        data[n]['oclc'].append('http://worldcat.org/oclc/' + resp_oclc)
    return(data)


def matchingISSN(data):
    for n in data:
        for issn in data[n]['issn']:
            url = issnx.format(issn)
            resp = requests.get(url).json()
            if 'list' in resp:
                resp_title = resp_lc = resp_oclc = ''
                doc_title = data[n]['title'][0]
                if 'title' in resp['list'][0]:
                    resp_title = resp['list'][0]['title']
                if 'lccn' in resp['list'][0]:
                    resp_lc = resp['list'][0]['lccn'][0]
                if 'oclcnum' in resp['list'][0]:
                    resp_oclc = resp['list'][0]['oclcnum'][0]
                title_score = fuzz.partial_ratio(doc_title, resp_title)
                if title_score < 80:
                    print(resp_title)
                    print(doc_title)
                    print(title_score)
                    if resp_lc not in data[n]['lccn']:
                        data[n]['lccn'].append(resp_lc)
                    if 'http://worldcat.org/oclc/' + resp_oclc not in data[n]['oclc']:
                        data[n]['oclc'].append('http://worldcat.org/oclc/' + resp_oclc)
                else:
                    if resp_lc not in data[n]['lccn']:
                        data[n]['lccn'].append(resp_lc)
                    if 'http://worldcat.org/oclc/' + resp_oclc not in data[n]['oclc']:
                        data[n]['oclc'].append('http://worldcat.org/oclc/' + resp_oclc)
    return(data)


def main():
    with open('data/docs.json', 'r') as fh:
        data = json.load(fh)
    keys = set()
    for n in data:
        for key in data.keys():
            keys.add(key)
    print(keys)
#    newdata = matchingISBN(data)
#    if data != newdata and newdata:
#        with open('data/docs.json', 'w') as fh:
#            json.dump(newdata, fh)


if __name__ == '__main__':
    main()
