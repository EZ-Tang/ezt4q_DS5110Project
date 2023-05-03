import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import requests
import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/stopwords')
except LookupError:
    nltk.download('stopwords')

CLIENT_ID = 'REDDIT_SECRET_ID'
SECRET_TOKEN = 'REDDIT_SECRET_TOKEN'
USERNAME = 'REDDIT_USERNAME'
PASSWORD = 'REDDIT_USERNAME'

print(dir())

"""
Helper Function
Finds the sentences with the given word
"""
def find_sentences_with_keyword(text, keyword):
    sentences = sent_tokenize(text)
    keyword_sentences = ""
    for sentence in sentences:
        if keyword in sentence.lower():
            keyword_sentences = keyword_sentences + sentence
    return keyword_sentences.lower()

"""
summarizes a given text, dropping all stopwords
"""
def nltk_summarize(text):
    sentences = sent_tokenize(text)
    words = [word_tokenize(sentence) for sentence in sentences]
    stop_words = set(stopwords.words('english'))
    filtered_words = [[word for word in sentence if word.lower() not in stop_words] for sentence in words]
    filtered_sentences = [' '.join(sentence) for sentence in filtered_words]
    text_object = nltk.Text(filtered_sentences)
    print("text_object")
    print(text_object)
    summary = text_object.generate()
    return summary


"""
CLIENT_ID, SECRET_TOKEN (str) are from RedditAPI
USERNAME, PASSWORD (str) is the account used to obain secret key
stock (str) is the name of the stock to be analyzed

"""
def analyze(stock, subreddit):

    # send a request for an OAuth token with username and password
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_TOKEN)
    data = {'grant_type': 'password',
            'username': USERNAME, # REMOVE
            'password': PASSWORD} # REMOVE
    headers = {'User-Agent': 'MyBot/0.0.1'}
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)
    TOKEN = res.json()['access_token']


    headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

    # Checks for a Response [200]
    requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)

    restrict = 1
    if (subreddit == ""):
        restrict = 0
        subreddit = "all"

    # Search for information about a particular stock
    params = {
        "q": stock,
        "sort": "hot",
        "limit": 20,
        "restrict_sr": restrict,
        "t": "month",
        "include_over_18": 1,
        "show": "all"
    }

    res = requests.get("https://oauth.reddit.com/r/" + subreddit + "/search",
                    headers=headers, params = params)
    df = pd.DataFrame()  # initialize dataframe
    # loop through each post retrieved from GET request
    for post in res.json()['data']['children']:
        # get relevant data to dataframe
        df = df.append({
            'subreddit': post['data']['subreddit'],
            'title': post['data']['title'],
            'selftext': post['data']['selftext'],
            'upvote_ratio': post['data']['upvote_ratio'],
            'ups': post['data']['ups'],
            'downs': post['data']['downs'],
            'score': post['data']['score']
        }, ignore_index=True)

    text = ""
    for i in df['selftext']:
        text = text + i

    if len(text) > 3800:
        text = text[0:3800]

    index = text.rfind('.')
    text = text[:index]
    print("TEXT")
    print(text)
    keyword_sentences = find_sentences_with_keyword(text, stock)
    print("KEYWORD SENTENCES")
    print(keyword_sentences)
    text = nltk_summarize(keyword_sentences)
    return text + "."