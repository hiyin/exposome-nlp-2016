from nlp_tokenizer import *

filtered_sent_dict=filter_sent(sent_tokenizer(transform(records)), chemicals)
extracted_relations = extract_filtered_relation(filtered_sent_dict, chemicals, diseases)

from textblob.classifiers import NaiveBayesClassifier


train = [
 ('rotenone model of Parkinson', 'no'),
 ('PDP) in a pesticide', 'no'),
 ('pesticide-induced gene mutations in the development of PD', 'no'),
 ('PD patients with pesticide', 'no'),
 ('pesticides, and describe the importance for DA neuron survival and PD', 'no'),
 ('pesticide-induced gene mutations may contribute to increasing susceptibility to PD', 'yes'),
 ('pesticides could lead to neurodegenerative diseases such as Parkinson', 'yes'),
 ('PD risk has been associated with insecticides, especially chlorpyrifos', 'yes'),
 ('pesticides in well water may contribute to PD', 'yes'),
 ("Pesticides have been associated with Parkinson's disease (PD", 'yes'),
 ("PD was associated with farming and the association with pesticide", 'yes'),
 ("pesticides or solvents is a risk factor for PD", 'yes'),
 ("pesticides is associated to PD", 'yes'),
 ("pesticides exposure factors and risk for PD", 'no'),
 ("pesticides or solvents is a risk factor for PD", 'yes')
]

test = [
 ("Parkinson's disease (PD) has been linked to pesticide exposures", 'yes'),
 ('pesticides is associated with an increased risk of developing PD', 'yes'),
 ("pesticides are involved in the aetiology of Parkinson's disease (PD),", 'yes'),
 ("Parkinson's disease phenyotype (PDP) in a pesticide", 'no'),
 ('PD and previous exposure to pesticide', 'no'),
 ('pesticide exposure and PD', 'no')
]



cl = NaiveBayesClassifier(train)
print(cl.accuracy(test))
print(cl.show_informative_features(10))

cl1 = cl.classify("pesticides, and describe the importance for DA neuron survival and PD")
cl2 = cl.classify('PD to exposure to pesticide')
cl3 = cl.classify('pesticides was highly significant in the studies in which PD')
cl4 = cl.classify("pesticide exposure is associated with an increased risk for developing Parkinson's disease (PD")
cl5 = cl.classify('PD risk was increased by exposure to any-type pesticide')
cl6 = cl.classify('pesticides is associated to PD')
cl7 = cl.classify('pesticides or in the extent of mitochondrial dysfunction, oxidative stress and neuronal loss may predispose individuals to PD')
cl8 = cl.classify("PD risk has been associated with insecticides, especially chlorpyrifos")
cl9 = cl.classify("pesticides, such as paraquat and maneb, in agriculture of less developed countries, the aim of our study was to investigate the involvement of nociceptin/orphanin-NOP and prodynorphin-KOP systems in a chronic paraquat and maneb animal model of Parkinson")
cl10 = cl.classify("Parkinson's disease (PD) and rural living, farming and pesticide")
cl11 = cl.classify("Parkinsonism and cholinesterase levels regarding to pesticide")
cl12 = cl.classify('pesticides and metals, are suggested risk factors for the development of typical late onset PD')




# print(cl1)
# print(cl2)
# print(cl3)
# print(cl4)
# print(cl5)
# print(cl6)
# print(cl7)
# print(cl8)
# print(cl9)
# print(cl10)
# print(cl11)
# print(cl12)


relation_results = {}

for pmid, tokens in extracted_relations.items():
    results = {}
    for token in tokens:
        relation = cl.classify(token)
        if relation not in results:
            results[relation] = [token]
        else:
            results[relation].append(token)

    relation_results[pmid] = results

print(relation_results)
