import math
from textblob import TextBlob as tb
from entrez_search import search, fetch_medline
from nlp_tokenizer import transform
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import re


results = search('Parkinson AND Pesticide')
id_list = results['IdList']
records = fetch_medline(id_list)
record_dict = transform(records)

def tf(word, blob):
    return blob.words.count(word) / len(blob.words)

def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob.words)

def idf(word, bloblist):
    return math.log(len(bloblist) / (1 + n_containing(word, bloblist)))

def tfidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)


bloblist = []
for pmid, abstract in record_dict.items():
    pattern = re.compile(r'\b(' + r'|'.join(stopwords.words('english')) + r')\b\s*', flags=re.IGNORECASE)
    abstract = pattern.sub('', abstract)

    print(abstract)

    bloblist.append(tb(abstract))

for i, blob in enumerate(bloblist):
    print("Top words in document {}".format(i + 1))
    scores = {word: tfidf(word, blob, bloblist) for word in blob.words}
    sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for word, score in sorted_words[:3]:
        print("\tWord: {}, TF-IDF: {}".format(word, round(score, 5)))