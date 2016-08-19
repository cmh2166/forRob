"""Take docs data stored as json, review text fields & pull out identifiers."""
import pprint
import json
import re

ids = ['oclc', 'issn', 'isbn', 'lc', 'lccn', 'dnb']


def addIDfields(data):
    for n in data:
        for identifier in ids:
            if identifier not in data[n]:
                data[n][identifier] = []
    return(data)


def grabIDs(data):
    """Parse text fields for any identifiers and move to new key/value pair."""
    for n in data:
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


def main():
    with open('data/docs.json', 'r') as fh:
        origdata = json.load(fh)
    data = addIDfields(origdata)
    newdata = grabIDs(data)
    if newdata:
        with open('data/docs.json', 'w') as fh:
            json.dump(newdata, fh)


if __name__ == '__main__':
    main()
