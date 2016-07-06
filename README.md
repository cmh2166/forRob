#Getty Sources (bibo:Document) to LoC Bibliographic Records

##Request
data/titles.txt.sorted.gz == ULAN titles extracted and sorted by source URI

From eyeballing, they look ... bad. Really bad.

What I want to accomplish is either:
  a) improve the value to the point where that's > 0
  b) demonstrate value == 0 and take it out of the LOD representation

Value additions:
  - link to LoC bibs, other?
  - Normalize titles and pull out non-Getty identifiers
  - do bibo:DocumentParts have any information to use for this? Seems not

##Getty bibo:Document information

433752 bibo:Document instances as of 5 July 2016 SPARQL query at vocab.getty.edu/sparql.

###fields:
| rdf:type | all bibo:Document |
| rdfs:seeAlso | always a URL of this structure: http://www.getty.edu/vow/AATSource?find=&logic=AND&note=&sourceid=[identifier]  |
| dcterms:created | date record was created  |
| dcterms:modified | date record was modified  |
| skos:changeNote | points to instances of prov:Activity, prov:Create, prov:Modify, http://example.com/base/Create, http://example.com/base/Modify (last two errors?) |
| dc:identifier | Getty identifiers only apparently (10 digits) |
| dcterms:title | title. All kinds of mess. |
| cc:license | All are http://opendatacommons.org/licenses/by/1.0/ |
| dcterms:license | same as cc:license. Why both? |
| void:inDataset | http://vocab.getty.edu/dataset/aat	has 44927, http://vocab.getty.edu/dataset/tgn	has 3567, http://vocab.getty.edu/dataset/ulan	has 62741 |
| bibo:shortTitle | Many are same as dcterms:title. Only 742 titles differ. Some URLs, could pull out for better data? |
| skos:note | variety of notes. Some identifiers - oclc links, ISBN/ISSNs, other. Unstructured. |

##Match title to LoC bibliographic title
