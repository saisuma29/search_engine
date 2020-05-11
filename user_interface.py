# NAME: SAISUMA DODDA
# UIN: 672075210
# NETID: sdodda4

import pickle
import math, string
import numpy as np
from flask import Flask, render_template, request, flash, redirect, url_for
import preprocessing
from preprocessing import tokenizer
from preprocessing import preprocessor

# function to load pickle files
def load_pickle(pklname):
    with open(pklname, 'rb') as f:
        return pickle.load(f)

# function to calculate document frequency for each word
def dfCalc():
    for word, urls in inverted_index.items():
        df[word] = len(urls)

# function to calculate inverse document frequency for each word
def idfCalc(max_pages):
    for word in inverted_index:
        idf[word] = math.log2((float(max_pages) / df[word]))
        for url in inverted_index[word]:
            inverted_index[word][url] *= idf[word]
            if url in url_length:
                url_length[url] += np.power(inverted_index[word][url], 2)
            else:
                url_length[url] = np.power(inverted_index[word][url], 2)

# function to preprocess query
def preprocess_query(query):
    query_df = {}
    query = query.lower()
    query_words = query.split(' ')

    for qword in query_words:
        text = preprocessor(qword)
        if(text == "a"):
            continue
        if text not in query_df:
            query_df[text] = 1
        else:
            query_df[text] += 1
    return query_df


# function to calculate cosine similarity score between user query and documents
def cosine_similarityCalc(query_df, top_cosine_similarity, idf, url_length, ranking_dict):
    
    inner_product = {}
    query_length = 0
    
    # compute inner product of document and user query
    for word in query_df:
        if word in inverted_index:
            for url in inverted_index[word]:
                if url in inner_product:
                    inner_product[url] += inverted_index[word][url] * idf[word] * query_df[word]
                else:
                    inner_product[url] = inverted_index[word][url] * idf[word] * query_df[word]
            query_length += np.power((query_df[word] * idf[word]), 2)   # finding query length
    
    cosine_similarity = []

    # calculating cosine similarity
    for url in url_length:
        if url in inner_product:
            similarity = inner_product[url] / math.sqrt(url_length[url] * query_length)
        else:
            similarity = 0
        cosine_similarity.append((similarity, url))
    cosine_similarity.sort(reverse= True)
    top_cosine_similarity.append(cosine_similarity[0:50])

# function to calculate page rank of pages based on the page rank scores
def rank_pages():
    ranked_pages = []
    for url, url_rank in page_rank_dict.items():
        ranked_pages.append((url_rank, url))
    ranked_pages.sort(reverse=True)

    for i,v in enumerate(ranked_pages):
        ranking_dict[v[1]] = i + 1

# function to find top 50 hits for the query based on cosine similarity and page rqank
def get_top_hits(top_cosine_similarity, ranking_dict):
    cosine_ranked = []      # list to store top hits based on cosine similarity and page rank

    for page in top_cosine_similarity:
        current_list = []
        for p in page:
            if p[1] in ranking_dict:
                current_list.append((ranking_dict[p[1]], p[1]))
        current_list.sort()
        cosine_ranked.append(current_list[0:50])
    cosine_ranked = cosine_ranked[0]

    for i in range(len(cosine_ranked)):
        cosine_ranked[i] = cosine_ranked[i][1]
    return cosine_ranked

# flask application to render templates of results
app = Flask(__name__)
app.secret_key = 'saisuma'

@app.route('/')
def search():
    return render_template('index.html')

top_results = []

@app.route('/', methods=['GET', 'POST'])
def get_input(i = 10):
    query = request.form['input_query']
    top_cosine_similarity = []
    query_words = preprocess_query(query)
    cosine_similarityCalc(query_words, top_cosine_similarity, idf, url_length, ranking_dict)
        
    top_results = get_top_hits(top_cosine_similarity, ranking_dict)
    # print(top_results)
    if request.method == 'POST':
        if request.form['submit_button'] == 'Search':
            return render_template('index.html', result = enumerate(top_results[:10]))
        if request.form['submit_button'] == 'Want more pages':
            pages = request.args.get('pages')
            print(pages)
            return render_template('index.html', result = enumerate(top_results[10:30]))
        if request.form['submit_button'] == 'Exit':
            flash('Exiting search engine..! Launch Again')
            return render_template('exit.html', msg = 'Exiting search engine..! Launch Again')
    else:
        return redirect(url_for('/'))

if __name__ == '__main__':
    inverted_index = load_pickle('inverted_index.pkl')
    page_rank_dict = load_pickle('pagerank.pkl')

    df = {}     # dictionary to store document frequency
    idf = {}    # dictionary to store inverse document frequency
    url_length = {}
    ranking_dict = {}
    max_pages = 5000    # max pages to be crawled
    dfCalc()
    idfCalc(max_pages)
    rank_pages()

    app.debug = True
    app.run()

