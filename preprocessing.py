# NAME: SAISUMA DODDA
# UIN: 672075210
# NETID: sdodda4

from nltk.corpus import stopwords
from nltk import PorterStemmer
import string, re
from bs4 import BeautifulSoup, Comment

stop_words = set(stopwords.words('english'))    # initializing stop words
ps = PorterStemmer()    # initializing porter stemmer

# function to tokenize the text
def tokenizer(content):
    words = ' '.join(re.findall('[a-zA-Z0-9]+', content))
    text = ''.join(word.lower() for word in words if not word.isdigit())    # to remove digits from the text
    words = text.split(' ')     # split on whitespace
    return words

# function to stem and check length of words
def preprocessor(word):
    if word not in stop_words:
        if ps.stem(word) not in stop_words and len(word) > 2:   # checking if the word is a stop word and length is greater than 2
            return ps.stem(word)
        return 'a'  
    return 'a' 

# function to eliminate SGML tags and comments from the text
def eliminate_tags(content):
    clean_text = []
    for text in content:
        if text.parent.name not in ['style', 'script', 'head', 'meta', '[document]'] and isinstance(text, Comment) == False:
            clean_text.append(text)
    return clean_text