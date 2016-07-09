"""Stored methods for ease of access."""
from lxml import etree
import re
import rdflib
import requests
from rdflib.namespace import RDF, DC, SKOS, DCTERMS
from SPARQLWrapper import SPARQLWrapper, JSON
import json

BIBO = rdflib.Namespace("http://purl.org/ontology/bibo/")
SRU = "http://lx2.loc.gov:210/lcdb?version=1.1"
SRU += "&operation=searchRetrieve&startRecord=1&recordSchema=marcxml"
issn = "&query=bath.issn="
isbn = "&query=bath.isbn="
# really bad matching here
title = "&query=dc.title="
ns = {'zs': "http://www.loc.gov/zing/srw/",
      'marc': 'http://www.loc.gov/MARC21/slim'}
numrec_xp = '/zs:searchRetrieveResponse/zs:numberOfRecords'
recID_xp = '/zs:searchRetrieveResponse/zs:records/zs:record/zs:recordData/'
recID_xp += 'marc:record/marc:controlfield[@tag="001"]'
title_xp = '/zs:searchRetrieveResponse/zs:records/zs:record/zs:recordData/'
title_xp += 'marc:record/marc:controlfield[@tag="001"]'
oclc_re = re.compile(r"http://www.worldcat.org/oclc/[0-9]{9}")


def getData():
    """Other methods too slow. Pull needed fields for biboDocs via SPARQL."""
    sparql = SPARQLWrapper("http://vocab.getty.edu/sparql")
    sparql.setQuery("""
        SELECT ?uri ?note ?title ?id ?shortTitle
        WHERE {
          ?uri a bibo:Document .
          OPTIONAL { ?uri dc:identifier ?id }
          OPTIONAL { ?uri dcterms:title ?title }
          OPTIONAL { ?uri skos:note ?note }
          OPTIONAL { ?uri bibo:shortTitle ?shortTitle }.
        }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    data = {}
    for result in results["results"]["bindings"]:
        uri = title = gettyID = shortTitle = note = ''
        if 'uri' in result:
            uri = result['uri']['value']
        if 'note' in result:
            note = result['note']['value']
        if 'title' in result:
            title = result['title']['value']
        if 'id' in result:
            gettyID = result['id']['value']
        if 'shortTitle' in result:
            shortTitle = result['shortTitle']['value']
        if uri not in data:
            data[uri] = {}
            data[uri]['note'] = [note]
            data[uri]['title'] = [title]
            data[uri]['id'] = [gettyID]
            data[uri]['shortTitle'] = [shortTitle]
        else:
            if 'note' in data[uri]:
                data[uri]['note'].append(note)
            else:
                data[uri]['note'] = [note]
            if 'title' in data[uri]:
                data[uri]['title'].append(title)
            else:
                data[uri]['title'] = [title]
            if 'id' in data[uri]:
                data[uri]['id'].append(gettyID)
            else:
                data[uri]['id'] = [gettyID]
            if 'shortTitle' in data[uri]:
                data[uri]['shortTitle'].append(shortTitle)
            else:
                data[uri]['shortTitle'] = [shortTitle]
    with open('data/output.json', 'w') as fh:
        json.dump(data, fh)


def matching():
    matched = {}
    match = False
    docs = rdflib.Graph.parse('data/docs.nt', format='nt')
    for doc in docs.subjects(RDF.type, BIBO.Document):
        for note in docs.objects(doc, SKOS.note):
            if 'ISSN' in note and not match:
                note = note.toPython().replace('ISSN', '')
                note = note.replace(':', '')
                note = re.sub(oclc_re, '', note)
                note = note.strip()
                results = requests.get(SRU + issn + note).text
                root = etree.fromstring(results)
                if root.xpath(numrec_xp, namespaces=ns)[0].text != 0:
                    bibid = root.xpath(recID_xp, namespace=ns)[0].text
                    matched[doc.toPython()] = "https://lccn.loc.gov/" + bibid
                    match = True
            elif 'ISBN' in note and not match:
                note = note.toPython().replace('ISBN', '')
                note = note.replace(':', '')
                note = re.sub(oclc_re, '', note)
                note = note.strip()
                results = requests.get(SRU + isbn + note).text
                root = etree.fromstring(results)
                if root.xpath(numrec_xp, namespaces=ns)[0].text != 0:
                    bibid = root.xpath(recID_xp, namespace=ns)[0].text
                    matched[doc.toPython()] = bibid
                    match = True
            elif 'http://www.worldcat.org/oclc/' in note and not match:
                note = note.strip()
                results = requests.get(note).status_code
                if results == '200':
                    matched[doc.toPython()] = note
                    match = True
            elif 'OCLC' in note and not match:
                note = note.toPython().replace('OCLC', '')
                note = note.replace(':', '')
                note = re.sub(oclc_re, '', note)
                note = note.strip()
                results = requests.get('http://www.worldcat.org/oclc/' +
                                       note).status_code
                if results == '200':
                    matched[doc.toPython()] = 'http://www.worldcat.org/oclc/' + note
                    match = True
            elif not match:
                for title_str in docs.objects(doc, DCTERMS.title):
                    note = note.strip()
                    results = requests.get(SRU + title_str + note).text
                    root = etree.fromstring(results)
                    if root.xpath(numrec_xp, namespaces=ns)[0].text != 0:
                        bibid = root.xpath(recID_xp, namespace=ns)[0].text
                        matched[doc.toPython()] = bibid
                        match = True


def main():
    getData()


if __name__ == '__main__':
    main()
