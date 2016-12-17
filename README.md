# exposome-nlp-2016
Exposome Informatics mini-Research Project 2016

System requirement
nltk - 3.2.1
pandas - 0.18.0
wordcloud - 1.2.1
inflect - 0.2.5

Author: Danqing (Angela) Yin

This folder contains a text mining system to extract exposure-disease association from PubMed to 
explore potential evidence in exposure-disease association and explore the implication of 
this information in completing exposome informatics infrastructure.

Main functionality of this system can be called in nlp_processor.py
entrez_search.py - retrieves information from PubMed
ml_classifier.py (defunct) - attempt to train classifier in association recognition
wordcloud_generator.py - generate wordcloud

This study employs PubMed’s E-utils and Python’s NLTK package to retrieve and extract disease-exposure associations from unstructured biomedical literature in recent 5 years.

## Information retrieval
Based on expert knowledge, measurable exposures from MyExposome.com were identified for two disease models, i.e. pesticides for Parkinson’s disease (PD) and ultraviolet light for osteoporosis (OP). These exposure and disease terms were mapped to corresponding Medical Subject Headings (MeSH) terms and jointed in Pubmed search query for retrieving MEDLINE abstract with high specificity.

## Information extraction
The disease and exposure entities were identified using dictionaries derived from SNOMED CT [13] and MeSH terms respectively, followed by regex matching to extract relevant sentence that contains disease-exposure co-occurrence. The measurable pesticides were also checked for reference against the list of registered pesticides from U.S. EPA [14], where referenced pesticides were added to exposure’s dictionary. The most frequent words were calculated to reflect word distribution in all abstracts. Further, relevant phrases containing disease-exposure co-occurrences in the sentence were extracted followed by detection of association, where patterns were used to extract the disease-exposure relation. Co-occurrence word matrix were built to show frequent combinations of the diseases and exposure. The most frequent words in all phrases were also computed to confirm the most commonly found associative words. The regex patterns were constructed to match the key associative word. For example, chemical <causes> disease, where the “cause” can be expressed as:
> (associated|associated with|cause[sd]|association|risk)

It is assumed that two co-occurring entities may be unrelated, but if they co-occur repeatedly, then they are likely related. The matching utilises joint regex in non-greedy manner, i.e. matching completes once the regex is matched to the sentence or phrase once. Accuracy is assured by whole-word only pattern to omit the word like “update” when searching for pattern like “PD”. Redundancy is avoided by checking that for no duplicates of extracted sentences or phrases.

Several techniques were adopted to increase the effectiveness of information retrieval, such as embedding boolean logic in search terms, use stopwords to filter out unimportant words from sentences, term variations were reduced by lemmatization to remove suffixes, and synonyms from ontologies and thesaurus were used to expand the coverage of regex. Likewise, information extraction uses sentence and word tokenization to enable more relevant matches within smaller units

