# NAME: SAISUMA DODDA
# UIN: 672075210
# NETID: sdodda4

from collections import deque
import threading, string, math
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import pickle
import preprocessing
import page_rank
from preprocessing import tokenizer, preprocessor, eliminate_tags
from page_rank import calculate_page_rank

# graph class to create an undirected graph
class graph():    
    def __init__(self, target_url):
        self.url = target_url
        self.out_edges = set()
        self.rank = 0
        self.num_neighbors = 0

    def get_edge(self, end_url):
        if end_url not in self.out_edges:
            self.out_edges.add(end_url)
            self.num_neighbors += 1
            
    def add_node(self, url, page_graph):
        if url not in page_graph:
            page_graph[url] = graph(url)
        
    def add_edge(self, start_url, end_url, page_graph):
        g.add_node(end_url, page_graph)
        page_graph[start_url].get_edge(end_url)

# function to process each url and calculate inverted index
def process_url(current_url, url_queue, urls_crawled, total_words, page_graph):
    page = requests.get(current_url)
    page_urls = []
    a_tags = []

    try:
        if(page.status_code == 200):    # status code 200 indicates page is retrieved successfully
            response = urlopen(current_url)
            soup = BeautifulSoup(response, 'lxml')        
            a_tags = soup.find_all('a', href=True)

    except Exception as e:
        print('Failed to connect {} due to {}: '.format(current_url, e))
        return 
    
    # extract all the links in a URL
    page_urls = []
    for tag in a_tags:
        href_link = tag.get('href')

        # if href_link is not None not any(ext in href_link for ext in except_extensions):
        if href_link.find('#'):
            href_link = href_link.split('#')
            href_link = href_link[0]

        if len(href_link) >= 1 and href_link[-1] != '/':
            href_link += '/'

        href_split = href_link.split('://')

        # checking for http and https 
        if len(href_split) > 1 and href_split[0][:4] == 'http':
            if len(href_split[0]) > 4 and href_split[0][4] == 's':
                href_split[0] = 'http'
            if href_split[1][:4] == "www.":
                href_split[1] = href_split[1][4:]
            href_bits = href_split[1].split('/')

            if domain in href_bits[0]:
                page_urls.append(href_split[0] + '://' + href_split[1])

        if len(href_split) == 1:
            if len(href_split[0]) > 1 and href_split[0][0] == '/':
                page_urls.append(current_url + href_split[0][1:])
                    
    # update the queue and add an edge from current URL to all URLs connected to it
    g.add_node(current_url, page_graph)     # add node in the undirected graph for the current url

    for c_url in page_urls:
        if c_url not in urls_crawled:
            urls_crawled.add(c_url)     # add current url to the set of crawled urls
            url_queue.append(c_url)     # add current url to the deque
        g.add_edge(current_url, c_url, page_graph)
    
    soup = BeautifulSoup(page.text, 'html.parser')      # parser to parse url content
    content = soup.find_all(text= True)  
    clean_text = eliminate_tags(content)    # to eliminate tags from the text

    for text in clean_text:
        text = text.strip()     # to remove extra spaces
        words = tokenizer(text)     # function to tokenize text

        for word in words:
            stem_word = preprocessor(word)      # function to preprocess words
            # calculating inverted index for each word
            if stem_word not in inverted_index:
                inverted_index[stem_word] = {}
                inverted_index[stem_word][current_url] = 1
                total_words[stem_word] = 1
            else:
                if current_url in inverted_index[stem_word]:
                    inverted_index[stem_word][current_url] += 1
                else:
                    inverted_index[stem_word][current_url] = 1
                total_words[stem_word] += 1
 
# function to save pickle 
def save_pickle(pklname, pkl_content):
    with open(pklname, 'wb') as f:
        pickle.dump(pkl_content, f)

# function to spider 5000 pages
def spider_pages(target_url):
    url_queue = deque()
    url_queue.append(target_url)
    urls_crawled = set()
    urls_crawled.add(target_url)
    page_count = 1
    total_words = {}
    page_graph = {}

    while page_count < max_pages and (len(url_queue) != 0):
        if len(url_queue) > 100:    # initializing thread crawlers using multithreading
            crawl_threads = [threading.Thread(target=process_url, args=([url_queue.popleft(), url_queue, urls_crawled, total_words, page_graph]), kwargs={}) for x in range(100)]
            for cthread in crawl_threads:
                cthread.start()     # starting crawler threads
            for cthread in crawl_threads:
                cthread.join()
            page_count += 100
        else:
            raw_url = url_queue.popleft()   # extract url from queue
            process_url(raw_url, url_queue, urls_crawled, total_words, page_graph)      # process each url
            page_count += 1
        # print(page_count)
    print('Finished crawling 5000 pages')
    page_rank_dict = calculate_page_rank(page_graph)    # calculate page rank
    
    save_pickle('crawled_urls.pkl', page_graph)
    save_pickle('inverted_index.pkl', inverted_index)
    save_pickle('pagerank.pkl', page_rank_dict)

# main
if __name__ == "__main__":
    target_url = 'https://www.cs.uic.edu/'
    domain = 'uic.edu'
    max_pages = 5000
    g = graph(target_url)
    inverted_index = {}
    except_extensions = ['mailto:', '.avi', '.ppt', '.gz', '.zip', '.tar', '.tgz', '.ico', '.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.JPG', '.mp4', '.svg']
    spider_pages(target_url)