#Getty Sources (bibo:Document) to LoC Bibliographic Records

##Request
data/titles.txt.sorted.gz == ULAN titles extracted and sorted by source URI

The data could be improved significantly, as at the moment it is not useful to machines, and much of it is not useful to humans either.

Value additions:
  - link to LoC bibs, other?
  - Normalize titles and pull out non-Getty identifiers
  - do bibo:DocumentParts have any information to use for this? Seems not? (has 3 properties at present - dcterms:isSourceOf links to bibo:Document, rdf:type gives bibo:DocumentPart, and bibo:locator gives the page number of place within an item, of some sort?) == bibo:DocumentPart not useful for reconciliation.

##Getty bibo:Document information

- 111,235* bibo:Document instances as of 5 July 2016 SPARQL query at vocab.getty.edu/sparql.
- AAT: 44,927 instances
- TGN: 3,567 instances
- ULAN: 62,741 instances

*updated - previous number was from a query that did not ask for distinct instances.

###fields:

| field | note|
| --- | --- |
| rdf:type | all bibo:Document |
| rdfs:seeAlso | always a URL of this structure: http://www.getty.edu/vow/AATSource?find=&logic=AND&note=&sourceid=[identifier] |
| dcterms:created | date record was created  |
| dcterms:modified | date record was modified  |
| skos:changeNote | points to instances of prov:Activity, prov:Create, prov:Modify, http://example.com/base/Create, http://example.com/base/Modify (last two errors?) |
| dc:identifier | Getty identifiers only (10 digits, no letters, confirmed) |
| dcterms:title | title. All kinds of mess. Can have multiple titles on 1 URI. |
| cc:license | All are http://opendatacommons.org/licenses/by/1.0/ |
| dcterms:license | same as cc:license. Why both? |
| void:inDataset | http://vocab.getty.edu/dataset/aat	has 44927, http://vocab.getty.edu/dataset/tgn	has 3567, http://vocab.getty.edu/dataset/ulan	has 62741 |
| bibo:shortTitle | Many are same as dcterms:title. Only 742 titles differ. Some URLs, could pull out for better data? |
| skos:note | variety of notes. Some identifiers - OCLC links, ISBN/ISSNs, other. Unstructured. Can have multiple notes on 1 URI. If you include inference available on SPARQL endpoint, this field includes URIs for instances of prov:Activity, prov:Create, prov:Modify, etc. (i.e. what is contained in skos:changeNote, above). |

##Match title to LoC bibliographic title
