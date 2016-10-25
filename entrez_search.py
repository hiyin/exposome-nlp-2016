# Adapted from https://gist.github.com/bonzanini/5a4c39e4c02502a8451d

from Bio import Entrez
from Bio import Medline
SEARCH_QUERY='Parkinson AND Pesticide'
MAX_RETURN='100'

def search(query):
    Entrez.email = 'your.email@example.com'
    handle = Entrez.esearch(db='pubmed',
                            sort='relevance',
                            retmax=MAX_RETURN,
                            retmode='xml',
                            mindate='2011/08',
                            maxdate='2016/08',
                            term=query)
    results = Entrez.read(handle)
    print('Total number of publications containing {0}: {1}'.format(SEARCH_QUERY, results['Count']))
    return results

def fetch_details(id_list):
    ids = ','.join(id_list)
    Entrez.email = 'your.email@example.com'
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    results = Entrez.read(handle)
    return results

def fetch_medline(id_list):
     ids = ','.join(id_list)
     handle = Entrez.efetch(db='pubmed',
                            rettype='medline',
                            retmode='text',
                            id=ids)
     results = Medline.parse(handle)
     return results

if __name__ == '__main__':
    search_query = '(Parkinson disease[Mesh] OR Parkinsonian Disorders[Mesh]) AND Pesticides[Mesh]'
    results = search(SEARCH_QUERY) # search_query = 'Parkinson AND Pesticide'
    id_list = results['IdList']
    papers = fetch_details(id_list)

    records = fetch_medline(id_list)

    for i, paper in enumerate(papers):
        print("%d) %s" % (i+1, paper['MedlineCitation']['Article']['ArticleTitle']))
    # Pretty print the first paper in full
    #import json
    #print(json.dumps(papers[0], indent=2, separators=(',', ':')))
    for i, record in enumerate(records):
        if 'AB' in record.keys():
            print("%d) %s" % (i+1, record['AB']))
