from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
from entrez_search import search, fetch_medline
import re
import inflect
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
inflect = inflect.engine()
lemmatize = WordNetLemmatizer()
import nltk
# nltk.download('all', halt_on_error=False)
# Solve above downloader issue https://github.com/nltk/nltk/issues/1283
import pandas


data = pandas.read_csv('/Users/dyin/Desktop/HaBIC/common_sql.csv', header=0)

agent_mesh = ["Acaricides",
"Chemosterilants",
"Fungicides",
"Herbicides",
"Defoliants",
"Insect Repellents",
"Insecticides",
"Molluscacides",
"Pesticide Residues",
"Pesticide Synergists",
"Rodenticides",
"Pesticides"]
agent_mesh_stem = [inflect.singular_noun(mesh) for mesh in agent_mesh]

chemicals = data["Chemical name"].tolist() + agent_mesh + agent_mesh_stem

# chemicals = [chemical.lower() for chemical in chemicals] + ["pesticide"]

results = search("Parkinson disease[Mesh] OR Parkinsonian Disorders[Mesh]) AND Pesticides[Mesh]")
id_list = results['IdList']
records = fetch_medline(id_list)
# Snomed_terms

subdisease = [
    "Juvenile Parkinson disease",
    "Juvenile Parkinson's disease",
    "Juvenile Parkinson's disease (disorder)",
    "Parkinsonism with orthostatic hypotension",
    "Parkinsonism with orthostatic hypotension (disorder)"]
diseases = [
    "Idiopathic Parkinson's disease"
    "Parkinson disease",
    "PD",
    "Parkinson's disease",
    "Parkinsons disease",
    "Primary Parkinsonism",
    "Idiopathic Parkinsonism",
    "Parkinson's disease (disorder)",
    "Parkinson's disease, NOS",
    "Paralysis agitans",
    "Idiopathic parkinsonism",
    "Primary parkinsonism",
    "Shaking palsy"] + subdisease


# diseases = ["PD", "parkinson", "parkin"] # becare of "updated"
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
    for pmid, abstract in record_dict.items():
        print(pmid, abstract)
        sent_dict[pmid] = sent_tokenize.tokenize(abstract) # {'pmid1': [sentence tokens],  'pmid2': [...]}
    # print(len(sent_dict))
    return sent_dict

def filter_sent(sent_dict, chemicals):
    found_chemicals = []
    filtered_sent_dict = {}

    for pmid, sent_tokens in sent_dict.items():
        filtered_tokens = []
        for token in sent_tokens:

            # match = re.search('parkinson+', token.lower)
            # print('Detected match in' + match)
            # ToDo: What about Parkinson abbrev e.g. PD, variation and implied associations etc
            # if 'parkinson' in token.lower() or 'pesticide' in token.lower():

            for chemical in chemicals:
                for disease in diseases:
                    # Method 1 (prefered behaviour):
                    dmatch = re.search(disease, token, flags=re.IGNORECASE)
                    cmatch = re.search(chemical, token, flags=re.IGNORECASE)
                    if (cmatch and dmatch) and (token not in filtered_tokens):

                        # print(match.group())
                        found_chemicals.append(chemical)
                        filtered_tokens.append(token)


                    else:
                        continue


            # if (any(chemical in token for chemical in chemicals))
            # for chemical in chemicals:
            #     if chemical in token.lower():
            #         print("Chemicals %s detected in sentence" % chemical)
            #         key_token = token
            #     else:
            #         continue
            #     filtered_tokens.append(key_token)

        filtered_sent_dict[pmid] = filtered_tokens

    print(set(found_chemicals))


    length_filteredsent = 0
    length_filteredarticle = 0
    for filtered_sent in filtered_sent_dict.values():
        if filtered_sent != []:
            length_filteredsent += len(filtered_sent)
            length_filteredarticle += 1
    print("The number of sentences after filtering is %s" % length_filteredsent)
    print("The number of PubMed literature after filtering is %s" % length_filteredarticle)


    print(filtered_sent_dict)
    # print(filtered_sent_dict.keys())




    return filtered_sent_dict

def match_word(input_string, string_list):
    words = re.findall(r'\w+', input_string)
    return [True for word in words if word in string_list]


def extract_filtered_relation(filtered_sent_dict, chemicals, diseases):
    extracted_phrase_dict = {}
    filtered_cooccur = []
    for pmid, sent_tokens in filtered_sent_dict.items():
        extracted_phrase = []
        for token in sent_tokens:
            for chemical in chemicals:
                for disease in diseases:

                    if not disease.isupper():
                        phrase1 = re.search('%s(.*)%s' % (chemical, disease), token, flags=re.IGNORECASE)
                        phrase2 = re.search('%s(.*)%s' % (disease, chemical), token, flags=re.IGNORECASE)
                    else:
                        phrase1 = re.search(r'%s(.*)\b%s\b' % (chemical, disease), token, flags=re.IGNORECASE)
                        phrase2 = re.search(r'\b%s\b(.*)%s' % (disease, chemical), token, flags=re.IGNORECASE)
                    # Eliminate duplicate/overlap phrases use any()
                    if (phrase1 and (not any(phrase1.group() in phrase for phrase in extracted_phrase))):
                        if (not any(phrase in phrase1.group() for phrase in extracted_phrase)):
                            extracted_phrase.append(phrase1.group())
                            filtered_cooccur.append((chemical, disease))

                    if (phrase2 and (not any(phrase2.group() in phrase for phrase in extracted_phrase))):
                        if (not any(phrase in phrase2.group() for phrase in extracted_phrase)):
                            extracted_phrase.append(phrase2.group())
                            filtered_cooccur.append((disease, chemical))

        extracted_phrase_dict[pmid] = extracted_phrase

    print("The number of co-occurence(s) is: %d with unique number: %d" % (len(filtered_cooccur), len(set(filtered_cooccur))))

    filtered_coocur_freq = {}
    for cooccur in filtered_cooccur:
        if cooccur not in filtered_coocur_freq:
            filtered_coocur_freq[cooccur] = 1
        else:
            filtered_coocur_freq[cooccur] += 1
    print("The frequency of all of co-occurrence (un-unique) is: ")
    print(filtered_coocur_freq)

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



def extract_causation(extracted_relations):
    extracted_cause_dict = {}
    for pmid, sent_tokens in filtered_sent_dict.items():
        extracted_cause = []
        for token in sent_tokens:
            nonstop_words = [word for word in word_tokenize(token) if word not in stopwords.words('english')]
            pos_tagged_words = pos_tag(nonstop_words)
            # n = nltk.chunk.ne_chunk(pos_tagged_words)
            # n.draw()
            for word, tag in pos_tagged_words:
                extracted_cause.append(word)
        
        extracted_cause_dict[pmid] = extracted_cause
    print("The extracted_cause_dict is: ")
    print(extracted_cause_dict)
    #         for chemical in chemicals:
    #             for disease in diseases:
    #                 if not disease.isupper():
    #                     cause1 = re.findall('%s(.*)%s' % (chemical, disease), token, flags=re.IGNORECASE)
    #                     cause2 = re.findall('%s(.*)%s' % (disease, chemical), token, flags=re.IGNORECASE)
    #                 else:
    #                     cause1 = re.findall(r'%s(.*)\b%s\b' % (chemical, disease), token, flags=re.IGNORECASE)
    #                     cause2 = re.findall(r'\b%s\b(.*)%s' % (disease, chemical), token, flags=re.IGNORECASE)
    #
    #                 if (cause1 and (not any(cause1.group() in cause for cause in extracted_cause))):
    #                         extracted_cause.append(cause1.group())
    #
    #                 if (cause2 and (not any(cause2.group() in cause for cause in extracted_cause))):
    #                         extracted_cause.append(cause2.group())
    #     extracted_cause_dict[pmid] = extracted_cause
    # print(extracted_cause_dict)

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

def remove_endwords(sent):
    sent_no_endwords = (re.sub(r'''(?x)      # VERBOSE mode
                 (             #
                  ^            # start of string
                  \w            # an alphanumeric character
                 \S*           # zero-or-more non-space characters
                 \s*           # followed by an alphanumeric character
                  )
                 |             # OR
                 (
                 \w            # an alphanumeric character
                 \S*           # zero-or-more non-space characters
                 \s*           # zero-or-more whitespaces
                 $             # end of string
                 )
                 ''',
            "",
            sent))
    return sent_no_endwords



if __name__ == '__main__':
    record_dict = transform(records)
    sent_dict = sent_tokenizer(record_dict)
    print("Start filtering sentence")
    filtered_sent_dict=filter_sent(sent_dict, chemicals)
    print("Start extracting relations")
    extracted_relations = extract_filtered_relation(filtered_sent_dict, chemicals, diseases)
    extract_causation(extracted_relations)

    # Todo: Does word tokenizer necessary?
    # filtered_word_dict=filtered_word_tokenizer(extracted_relations)
    # word_dict = word_tokenizer(record_dict)
    # postag_dict = pos_tagger(word_dict)
    # named_entity_dict = entity_recognizer(postag_dict)




