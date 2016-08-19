# Getty Sources (bibo:Document) to LoC Bibliographic Records

## Request

The data could be improved significantly, as at the moment it is not useful to machines, and much of it is not useful to humans either.

Value additions:
  - link to LoC bibs, other?
  - Normalize titles and pull out non-Getty identifiers
  - do bibo:DocumentParts have any information to use for this? Seems not?

## Getty bibo:Document information

Following numbers based on 19 August 2016 SPARQL query at vocab.getty.edu/sparql.

### bibo:Document with Inference

434726 bibo:Document & bib:DocumentPart instances

### bibo:Document without Inference

111467 bibo:Document instances

- AAT: 45023 instances
- TGN: 3598 instances
- ULAN: 62846 instances

### bibo:DocumentPart without Inference

4303389 bibo:Document instances

- AAT:  230448 instances
- TGN: 3641279 instances
- ULAN: 431662 instances

## Data Files



### fields

#### bibo:Document

| field            | note                                                |
| ---              | ---                                                 |
| rdf:type         | always bibo:Document only                           |
| rdfs:seeAlso     | always URL with this structure: http://www.getty.edu/vow/AATSource?find=&logic=AND&note=&sourceid=[identifier] |
| dcterms:created  | date record was created                             |
| dcterms:modified | date record was modified                            |
| skos:changeNote  | points to instances of prov:Activity, prov:Create, prov:Modify, http://example.com/base/Create, http://example.com/base/Modify (last two errors?) |
| dc:identifier    | Getty identifiers only (10 digits, no letters)      |
| dcterms:title    | Titles. Messy. Can have multiple titles on 1 URI    |
| cc:license       | All are http://opendatacommons.org/licenses/by/1.0/ |
| dcterms:license  | same as cc:license. Why both?                       |
| void:inDataset   | <http://vocab.getty.edu/dataset/aat>, <http://vocab.getty.edu/dataset/tgn>, <http://vocab.getty.edu/dataset/ulan> |
| bibo:shortTitle  | Most are same as dcterms:title. Only 742 titles differ. Some URLs, could pull out for better data? |
| skos:note        | variety of notes. Some identifiers - OCLC links, ISBN/ISSNs, other. Unstructured. Can have multiple notes on 1 URI. If you include inference available on SPARQL endpoint, this field includes URIs for instances of prov:Activity, prov:Create, prov:Modify, etc. (i.e. what is contained in skos:changeNote, above). |

#### bibo:DocumentPart

(has 3 properties at present - dcterms:isSourceOf links to bibo:Document, rdf:type gives bibo:DocumentPart, and bibo:locator gives the page number of place within an item, of some sort?) == bibo:DocumentPart not useful for reconciliation.

| field               | note                                           |
| ---                 | ---                                            |
| rdf:type            | always bibo:DocumentPart only                  |
| dcterms:isPartOf    | required by BIBO. Points to bibo:Document URI  |
| bibo:locator        | literal. Not sure what locations are captured. |

## Enhancements, Outputs & Remarks

### Pull Out and Normalize non-Getty Identifiers in bibo:Document

Identifiers appear in:

- title / <http://purl.org/dc/terms/title>
- shortTitle / <http://purl.org/ontology/bibo/shortTitle>
- note / <http://www.w3.org/2004/02/skos/core#note>

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

### Link bibo:Document URIs to LoC Bibliographic records

Link to the LCCN, not to the LoC Voyager instance bib ID.


### Normalize Titles (dcterms:title and bibo:shortTitle) in bibo:Document


### Normalize Locators in bibo:DocumentParts
