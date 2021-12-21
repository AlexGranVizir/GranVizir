from tika import parser
import spacy
from spacy_readability import Readability
import textstat
import os
import numpy as np
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
from collections import Counter

import matplotlib.pyplot as plt


nlp = spacy.load('en')
read = Readability()
nlp.add_pipe(read, last=True)

base_path = "./samples/BRs/"
target_path = "./samples/target/"
master_file = "./samples/master_data_file.csv"

for root, dirs, files in os.walk(base_path):
    print("Total files found: {}".format(len(files)))


for root, dirs, file_target in os.walk(target_path):
    print("Total files found: {}".format(len(file_target)))

# stopwords
stopwords = set(STOPWORDS)
stopwords.update(["liquid"],["yes"],["Will"], ["BR SOLA MiFid"], ["Pellizzoni"], ["Index"],
                 ["Comment"], ["Date"], ["Derivatives"], ["Phase"], ["Class"],
                 ["classification"], ["annually"], ["vs"], ["classes"], ["liquidity"],
                 ["change", "euro", "BR", "key"])


my_keywords = ["order", "implied", "trade", "price", "quantity", "trader", "instrument", "account", "configurable"]

my_cols = ["doc_key", "estimate"]
my_cols = my_cols
word_cols = []

my_df = pd.DataFrame(columns=my_cols)
target_df = pd.DataFrame(columns=my_cols).drop(columns='estimate')

master_data_df = pd.read_csv(master_file)
master_data_df.set_index('Key',inplace=True)

# Loop, Parse data from files in the past
for i in range(1, len(files)+1):
    file = files[i-1]
    print("Parsing file: ", file)
    file_data = parser.from_file(base_path+file)

    # Get files text content
    text = file_data['content']
    doc = nlp(text)

    words = [token.text for token in doc if token.is_stop != True and token.is_punct != True and token.text.isalpha()
             and token.text not in my_cols and token.text not in stopwords]
    # words = [token.text for token in doc if token.is_stop != True and token.is_punct != True and token.text in my_keywords and token.text not in stopwords]

    # filename key
    doc_key = {'doc_key': file.split("]")[0][1:]}

    # original estimation
    est = {'estimate': master_data_df.loc[doc_key["doc_key"]].Estimate}

    # extract keyword frequency
    # update colums in dataframe
    for term in words:
        if term not in word_cols:
            my_df[term] = 'NaN'
            target_df[term] = 'NaN'
            word_cols.append(term)

    word_freq = Counter(words)

    # row
    row = {**doc_key, **est, **word_freq}
    my_df = my_df.append(row, ignore_index=True)

# Parse data for target
file_data = parser.from_file(target_path+file_target[0])

# Get files text content
text = file_data['content']
doc = nlp(text)
words = [token.text for token in doc if token.is_stop != True and token.is_punct != True and token.text.isalpha()
         and token.text not in my_cols and token.text not in stopwords]
# words = [token.text for token in doc if token.is_stop != True and token.is_punct != True and token.text in my_keywords and token.text not in stopwords]
# filename key
doc_key = {'doc_key': file_target[0].split("]")[0][1:]}


# extract keyword frequency
# update colums in dataframe
for term in words:
    if term not in word_cols:
        my_df[term] = 'NaN'
        target_df[term] = 'NaN'
        word_cols.append(term)

word_freq = Counter(words)

# row
row = {**doc_key, **word_freq}
target_df = target_df.append(row, ignore_index=True)


# dump
my_df.to_csv("./data/processed_data.csv")
target_df.to_csv("./data/processed_target_data.csv")

