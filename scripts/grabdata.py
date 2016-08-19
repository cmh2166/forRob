"""Stored methods for ease of access."""
import rdflib
import json

BIBO = rdflib.Namespace("http://purl.org/ontology/bibo/")


def getData():
    """Other methods incomplete/slow. Pull fields for biboDocs via dumps."""
    g = rdflib.Graph().parse("data/ULANOut_Full.nt", format="nt")

    result = g.query(
        """PREFIX bibo: <http://purl.org/ontology/bibo/>
        PREFIX dc: <http://purl.org/dc/elements/1.1/>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT DISTINCT ?uri ?id ?title ?note ?shortTitle
            WHERE {
              ?uri a bibo:Document .
              OPTIONAL { ?uri dc:identifier ?id }
              OPTIONAL { ?uri dcterms:title ?title }
              OPTIONAL { ?uri skos:note ?note }
              OPTIONAL { ?uri bibo:shortTitle ?shortTitle }.
            }
        """)
    data = {}
    for row in result:
        uri = title = gettyID = shortTitle = note = ''
        if row['uri']:
            uri = row['uri'].toPython()
        if row['note']:
            note = row['note'].toPython()
        if row['title']:
            title = row['title'].toPython()
        if row['id']:
            gettyID = row['id'].toPython()
        if row['shortTitle']:
            shortTitle = row['shortTitle'].toPython()
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
    with open('data/ulan.json', 'w') as fh:
        json.dump(data, fh)
    return(data)


def main():
    """Grabbing AAT, TGN, ULAN bibo:Documents, ignoring bibo:DocumentParts."""
    with open('data/docs.json', 'r') as fh:
        data = json.load(fh)
    parseData(data)

if __name__ == '__main__':
    main()
