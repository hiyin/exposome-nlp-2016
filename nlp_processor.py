from nltk.tokenize import sent_tokenize, word_tokenize
import nltk.data
from nltk import pos_tag
from entrez_search import search, fetch_medline
import re
import inflect
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
from nltk.tokenize import WordPunctTokenizer
punctword_tokenizer = WordPunctTokenizer()
inflect = inflect.engine()
WNL = WordNetLemmatizer()
# nltk.download('all', halt_on_error=False)
# Solve above downloader issue https://github.com/nltk/nltk/issues/1283
import pandas
import operator
from word_cloud import draw_wordcloud
pickle_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

stop_words = set(stopwords.words('english'))
stop_words.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}',
                   '%', '-', "),", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]) # remove it if you need punctuation

# results = search("ultraviolet rays[MeSH Terms] AND osteoporosis[MeSH Terms]")
def initialize_data(topic):
    if topic == "OP":
        results = search("(Ultraviolet rays[MeSH Terms] OR Sunlight[Mesh]) AND (Osteoporosis[MeSH Terms]")
        records = fetch_medline(results['IdList'])

        agent_mesh = ["Ultraviolet Rays","Ultra-Violet Rays","Ultra-Violet Rays","Ultra Violet Rays","Actinic Rays",
                      "Ultraviolet Light","Ultraviolet","UV Light","UV","Black Lights","Ultraviolet Black Lights"]
        expanded_terms = ["Sun", "Sunshine", "Sunlight", "Ultraviolet Radiation", "UVA", "UVB", "Ultraviolet A", "Ultraviolet B"]
        chemicals = agent_mesh + [mesh.rstrip("s") for mesh in agent_mesh] + expanded_terms
        diseases = ["osteoporosis","osteoporosis, NOS", "osteoporoses"]
    if topic == "PD":
        data = pandas.read_csv('/Users/dyin/Desktop/Semester 2/HaBIC/common_sql.csv', header=0)

        agent_mesh = ["Acaricides", "Chemosterilants", "Fungicides", "Herbicides", "Defoliants", "Insect Repellents",
                      "Insecticides", "Molluscacides", "Pesticide Residues", "Pesticide Synergists", "Rodenticides",
                      "Pesticides"]
        chemicals = data["Chemical name"].tolist() + agent_mesh + [inflect.singular_noun(mesh) for mesh in agent_mesh]

        results = search("(Parkinson disease[Mesh] OR Parkinsonian Disorders[Mesh]) AND Pesticides[Mesh]")
        records = fetch_medline(results['IdList'])

        diseases = ["Idiopathic Parkinson's disease", "Parkinson disease", "PD", "Parkinson's disease",
                    "Parkinsons disease", "Primary Parkinsonism", "Idiopathic Parkinsonism", "Parkinson's disease (disorder)",
                    "Parkinson's disease, NOS", "Paralysis agitans", "Idiopathic parkinsonism", "Primary parkinsonism", "Shaking palsy"]

    return records, chemicals, diseases

def transform(records):
    record_dict = {}
    for i, record in enumerate(records):

        if 'AB' not in record.keys():
            pass
        else:
            abstract = str(record['AB'])
            title = str(record['TI'])
            pmid = str(record['PMID'])
            record_dict[pmid] = abstract
    return record_dict



# ToDo: when to use sentence tokens?
def sent_tokenizer(record_dict):
    sent_dict = {}
    sent_tokenize = nltk.data.load('tokenizers/punkt/english.pickle')
    join_sent = ''
    for pmid, abstract in record_dict.items():
        # print(pmid, abstract)
        sent_dict[pmid] = sent_tokenize.tokenize(abstract)
        join_sent = join_sent + abstract

    # print(len(sent_dict))
    draw_wordcloud(join_sent)
    return sent_dict

def filter_sent(sent_dict, chemicals, diseases):
    dregexes = '(?:%s)' % '|'.join(diseases)
    cregexes = '(?:%s)' % '|'.join(chemicals)
    print(cregexes)
    sum_sent = 0
    found_chemicals = []
    filtered_sent_dict = {}
    flt_co_dict = {}
    for pmid, sent_tokens in sent_dict.items():
        total_sent = len(sent_tokens)
        flt_co = []
        filtered_tokens = []
        for token in sent_tokens:
            dmatch = re.search(dregexes, token) ## Turn down for PD
            cmatch = re.search(cregexes, token, flags=re.IGNORECASE)

            if ((cmatch) and (dmatch)) and (token not in filtered_tokens):
                found_chemicals.append(cmatch.group(0))
                filtered_tokens.append(token)
                flt_co.append((dmatch.group(0), cmatch.group(0)))
            else:
                continue
        sum_sent += total_sent
        filtered_sent_dict[pmid] = filtered_tokens
        flt_co_dict[pmid] = flt_co
    print("The following agent(s) are found in matched sentences: " + ', '.join(set(found_chemicals)))


    length_filteredsent = 0
    length_filteredarticle = 0
    for filtered_sent in filtered_sent_dict.values():
        if filtered_sent != []:
            length_filteredsent += len(filtered_sent)
            length_filteredarticle += 1


    print("The total number of unfiltered sentences is %s" % sum_sent)
    print("The number of sentences after filtering is %s" % length_filteredsent)
    print("The number of PubMed literature after filtering is %s" % length_filteredarticle)


    print(filtered_sent_dict)
    co_freq_dict, sum_co_freq_dict = co_counter(flt_co_dict)
    print("The frequency of all of co-occurrence (un-unique) is: ")
    print(co_freq_dict)
    print(sorted(sum_co_freq_dict.items(), key=operator.itemgetter(1)))
    print("The total number of co-occurrence(s) is: %d with %d unique set of co-occurrence" % (sum(sum_co_freq_dict.values()), len(sum_co_freq_dict.keys())))


    return filtered_sent_dict

def co_counter(flt_co_dict):
    co_freq_dict = {}
    for pmid, co_tups in flt_co_dict.items():
        co_freq = {}
        for co in co_tups:
            if co not in co_freq:
                co_freq[co] = 1
            else:
                co_freq[co] += 1

        if pmid not in co_freq_dict:
            co_freq_dict[pmid] = co_freq

    sum_co_freq_dict = {}
    for freq_dict in co_freq_dict.values():
        for co, freq in freq_dict.items():
            if co not in sum_co_freq_dict:
                sum_co_freq_dict[co] = freq
            else:
                sum_co_freq_dict[co] += freq

    return co_freq_dict,sum_co_freq_dict

def match_word(input_string, string_list):
    words = re.findall(r'\w+', input_string)
    return [True for word in words if word in string_list]



def extract_filtered_relation(filtered_sent_dict, chemicals, diseases):
    cregexes = '(?:%s)' % '|'.join(chemicals)
    dregexes = '(?:%s)' % '|'.join(diseases)
    extracted_phrase_dict = {}
    for pmid, sent_tokens in filtered_sent_dict.items():
        extracted_phrase = []
        for token in sent_tokens:
            phrase1 = re.search('%s(.*)%s' % (cregexes, dregexes), token, flags=re.IGNORECASE)
            phrase2 = re.search('%s(.*)%s' % (dregexes, cregexes), token, flags=re.IGNORECASE)
            if (phrase1 and (not any(phrase1.group() in phrase for phrase in extracted_phrase))):
                if (not any(phrase in phrase1.group() for phrase in extracted_phrase)):
                    extracted_phrase.append(phrase1.group())
            if (phrase2 and (not any(phrase2.group() in phrase for phrase in extracted_phrase))):
                if (not any(phrase in phrase2.group() for phrase in extracted_phrase)):
                    extracted_phrase.append(phrase2.group())

        extracted_phrase_dict[pmid] = extracted_phrase


    length_extractedphrase = 0
    length_extractedarticle = 0
    for extracted_phrase in extracted_phrase_dict.values():
        if extracted_phrase != []:
            length_extractedphrase += len(extracted_phrase)
            length_extractedarticle += 1
    print("The number of phrases extracted after filtering is %s" % length_extractedphrase)
    print("The number of PubMed literature after extracting phrase is %s" % length_extractedarticle)

    print(extracted_phrase_dict)
    return extracted_phrase_dict


def word_tokenizer(record_dict):
    word_dict = {}
    for pmid, abstract in record_dict.items():
        word_dict[pmid] = word_tokenize(abstract)
    print(len(word_dict))
    # print(word_dict['23987116'])
    return word_dict


def filtered_word_tokenizer(filtered_sent_dict):
    filtered_word_dict = {}
    for pmid, sent_tokens in filtered_sent_dict.items():
        word_tokens = []
        for sent_token in sent_tokens:
            word_token = word_tokenize(sent_token) # token of single sentence
            word_tokens = word_tokens + word_token
        filtered_word_dict[pmid] = word_tokens

    print(filtered_word_dict)
    return filtered_word_dict

def extract_causation(extracted_relations_dict):
    cregexes = '(?:%s)' % '|'.join(chemicals)
    dregexes = '(?:%s)' % '|'.join(diseases)
    extracted_cause_dict = {}
    extracted_causative_phrase = {}
    causative_phrases_freq = {}
    for pmid, sent_tokens in extracted_relations_dict.items():
        causative_phrases = []
        for token in sent_tokens:
            # Trial new puctword tokenizer to avoid "'s" occurences
            nonstop_words = [word for word in punctword_tokenizer.tokenize(token) if word.lower() not in stop_words]
            # n = nltk.chunk.ne_chunk(pos_tag(nonstop_words))
            # n.draw()
            for word in nonstop_words:
                if WNL.lemmatize(word) not in extracted_cause_dict:
                    extracted_cause_dict[WNL.lemmatize(word)] = 1
                else:
                    extracted_cause_dict[WNL.lemmatize(word)] += 1


            causative_phrase = re.search(r"(associated|associated with|cause[sd]|association|risk)", token)
            if causative_phrase:
                causative_phrases.append(causative_phrase.group())

        extracted_causative_phrase[pmid] = causative_phrases
    print("The extracted phrases are: ")
    print(extracted_causative_phrase)

    unique_causes_freq = {}
    num_paper_has = 0
    for pmid, phrases in extracted_causative_phrase.items():
        if phrases != []:
            num_causes = len(phrases)
            num_paper_has += 1
        for phrase in phrases:
            if phrase not in unique_causes_freq:
                unique_causes_freq[phrase] = num_causes
            else:
                unique_causes_freq[phrase] += num_causes

    print("The number of papers has shown real causative words is %s, and the freq of extracted phrases are: "% num_paper_has)
    print(unique_causes_freq)





    return extracted_cause_dict


def removekey(d):
    r = dict(d)
    if len(d) < 100:
        cutoff = 0
    else:
        cutoff = 10
    for key, value in d.items():
        if value < cutoff:
           del r[key]
    return r


def pos_tagger(word_dict):
    postag_dict = {}
    for pmid, tokens in word_dict.items():
        postag_dict[pmid] = pos_tag(tokens)
    print(postag_dict['23987116'])
    return postag_dict


def entity_recognizer(postag_dict):
    entity_dict = {}
    for pmid, tagged_tokens in postag_dict.items():
        entity_dict[pmid] = nltk.chunk.ne_chunk(tagged_tokens)
    print(entity_dict['23987116'])
    return entity_dict

if __name__ == '__main__':
    print("Start collecting data")
    records, chemicals, diseases = initialize_data("OP")
    record_dict = transform(records)
    sent_dict = sent_tokenizer(record_dict)
    print("Start filtering sentence")
    filtered_sent_dict=filter_sent(sent_dict, chemicals, diseases)
    print("Start identifying entities and extracting relations")
    extracted_relations = extract_filtered_relation(filtered_sent_dict, chemicals, diseases)
    extracted_causes = extract_causation(extracted_relations)
    frequent_causes = removekey(extracted_causes)
    sorted_causes = sorted(frequent_causes.items(), key=operator.itemgetter(1))
    print(sorted_causes)

    # Todo: Does word tokenizer necessary?
    # filtered_word_dict=filtered_word_tokenizer(extracted_relations)
    # word_dict = word_tokenizer(record_dict)
    # postag_dict = pos_tagger(word_dict)
    # named_entity_dict = entity_recognizer(postag_dict)




