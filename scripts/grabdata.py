"""Second attempt at better handling of grabbing data."""
import requests
import rdflib
import xml
GettySPARQL = "http://vocab.getty.edu/sparql.json?query=SELECT+DISTINCT+%3Fdoc\
               %0D%0AWHERE+%7B%0D%0A++%3Fdoc+a+bibo%3ADocument+.%0D%0A%7D\
               &_implicit=false&_equivalent=false&_form=%2Fsparql"


def getURIs():
    """Other methods incomplete/slow. Pull fields for biboDocs via dumps."""
    URIs = []
    results = requests.get(GettySPARQL).json()

    if len(results["results"]["bindings"]) != 111467:
        print('Error with Getty SPARQL Endpoint Return.')
    else:
        for result in results["results"]["bindings"]:
            URIs.append(result["doc"]["value"])
    return(URIs)


def grabGraph(URIs):
    """Get graph for each URI, save to file."""
    data = rdflib.Graph().parse("data/data.nt", format="nt")
    num = len(URIs)
    print("Grabbing fresh data.")
    n = 55000
    for URI in URIs[55000:]:
        n += 1
        print(n, num)
        try:
            data.parse(URI)
        except xml.sax._exceptions.SAXParseException:
            print("Error: " + URI)
        if n % 100 == 0:
            data.serialize(destination='data/data.nt', format='nt')
    data.serialize(destination='data/data.nt', format='nt')
    return(data)


def main():
    """Grabbing AAT, TGN, ULAN bibo:Documents, ignoring bibo:DocumentParts."""
    URIs = getURIs()
    grabGraph(URIs)

if __name__ == '__main__':
    main()
