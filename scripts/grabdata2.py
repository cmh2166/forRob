"""Second attempt at better handling of grabbing data."""
import requests
import rdflib
import os.path
from rdflib.namespace import DC as dc
from rdflib.namespace import DCTERMS as dct
from rdflib.namespace import SKOS as skos
from rdflib.namespace import OWL as owl
import re
bibo = rdflib.Namespace("http://purl.org/ontology/bibo/")
GettySPARQL = "http://vocab.getty.edu/sparql.json?query=PREFIX+GVP%3A+%3Chttp%3\
               A%2F%2Fvocab.getty.edu%2Fontology%23%3E%0D%0ASELECT+DISTINCT+%3F\
               doc+WHERE%0D%0A%7B%0D%0A+++%3Fdoc+a+bibo%3ADocument+.%0D%0A%7D\
               &_implicit=false&_equivalent=false&_form=%2Fsparql"


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
                    print(oclc)




        for field in (data[n]['title'] + data[n]['shortTitle'] + data[n]['note']):
            if '.org/oclc' in field.lower():
                oclc_split = field.lower().split('worldcat.org/oclc/')[1]
                oclc = re.split("\n| ", oclc_split.replace(':', '').strip())[0]
                if oclc not in data[n]['oclc']:
                    data[n]['oclc'].append(oclc)
            if 'issn' in field.lower() and not 'issner' in field.lower() and not 'issnik' in field.lower():
                issn_split = field.lower().split('issn')[1]
                issn = re.split("\n| ", issn_split.replace(':', '').strip())[0].strip('.')
                if issn not in data[n]['issn']:
                    data[n]['issn'].append(issn)
            if 'isbn' in field.lower():
                isbn_split = field.lower().split('isbn')[1]
                isbn = re.split("\n| ", isbn_split.replace(':', '').strip())[0]
                if isbn not in data[n]['isbn']:
                    data[n]['isbn'].append(isbn)
            if 'd-nb.info/' in field.lower():
                dnb_split = field.lower().split('d-nb.info/')[1]
                dnb = re.split("\n| ", dnb_split.strip())[0].split('/')[0]
                if dnb not in data[n]['dnb'] and dnb is not 'gnd':
                    data[n]['dnb'].append(dnb)
            if 'lccn' in field.lower():
                lccn_split = field.lower().split('lccn')[1].strip()
                lccn = re.split("\n|;|:|/|\r", lccn_split.strip())[0].strip()
                lccn = lccn.replace(' ', '').replace('-', '')
                if lccn not in data[n]['lccn'] and lccn:
                    data[n]['lccn'].append(lccn)
    return(data)


def getURIs():
    """Other methods incomplete/slow. Pull fields for biboDocs via dumps."""
    URIs = set()
    results = requests.get(GettySPARQL).json()

    if len(results["results"]["bindings"]) != 111467:
        print('Error with Getty SPARQL Endpoint Return.')
    else:
        for result in results["results"]["bindings"]:
            URIs.add(result["doc"]["value"])
    return(URIs)


def grabGraph(URIs):
    """Get graph for each URI, save to file."""
    data = rdflib.Graph()
    num = len(URIs)
    if os.path.exists("data/data.nt"):
        data.parse("data/data.nt", "nt")
    else:
        print("Grabbing fresh data.")
        n = 0
        for URI in URIs:
            n += 1
            print(n, num)
            data.parse(URI)
            if n % 1000 == 0:
                data.serialize(destination='data/data.nt', format='nt')
        data.serialize(destination='data/data.nt', format='nt')
    return(data)


def main():
    """Grabbing AAT, TGN, ULAN bibo:Documents, ignoring bibo:DocumentParts."""
    URIs = getURIs()
    data = grabGraph(URIs)

if __name__ == '__main__':
    main()
