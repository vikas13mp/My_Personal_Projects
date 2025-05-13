#importing libraries
from flask import Flask, render_template, request, redirect
from datetime import datetime
import numpy as np
import re
import nltk
nltk.download('punkt')
nltk.download('stopwords')
import joblib
import pickle
import sklearn
import requests
from bs4 import BeautifulSoup
import re, sys
import pandas as pd
import time
import string
import os
import pandas as pd
import numpy as np

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import classification_report
from sklearn.linear_model import SGDClassifier

#Web Scraping for collecting the data from website 
pd.set_option('max_colwidth', None)
def webscraping(x):
    site = x.split('.')[1]
    if site == 'flipkart':
        if (x.endswith('FLIPKART')):
            x = x.replace("/p/", "/product-reviews/") + '&page=1'
        else:
            x = x.split('&store=')[0].replace("/p/", "/product-reviews/") + '&page=1'
    elif site == 'amazon':
        if (x.find('_encoding')!=-1):
            x = x.split('?_encoding=')[0].replace("/dp/", "/product-reviews/") +'ie=UTF8&reviewerType=all_reviews' + '&pageNumber=1'
        else:
            x = x.split('/ref=')[0].replace("/dp/", "/product-reviews/") +'/ie=UTF8&reviewerType=all_reviews' + '&pageNumber=1'
    url = x
    return scraper(url)

#Creating Soup object from URL
def getsoup(url):
    response = requests.get(url, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'})
    Status_Code = response.status_code
    print(url)
    print(Status_Code)
    
    if Status_Code == 200:
      soup = BeautifulSoup(response.content, features="lxml")
    else:
      soup = getsoup(url)
    return soup 

#Get Last Page number
def getLastPageNumber(soup, site):
    pageNumber = []
    if site == 'flipkart':
        review_number = int(soup.find("span", "_2_R_DZ").text.strip().replace(',', '').split()[-2])
        if review_number <=10:
            lastPage = 1
        else:
            link = soup.find(attrs={"class": "_2MImiq _1Qnn1K"})
            pageNumber = link.find('span').text.strip().replace(',', '').split()
            lastPage1 = pageNumber[len(pageNumber)-1]
            lastPage = int(lastPage1)
    elif site == 'amazon':
        reviews = soup.find("div", {"data-hook":"cr-filter-info-review-rating-count"})
        review_number = int(reviews.text.strip().replace(',', '').split()[-3])
        if review_number <=10:
            lastPage = 1
        else:
            lastPage = review_number // 10
    if lastPage > 500:
        lastPage = 2
    return lastPage

# Function to create a list of URLs for all the review pages for a product

def geturllist(url, lastPage):
    urllistPages = []
    url = url[:-1]
    for i in range(1,lastPage+1):
      urllistPages.append (url + str(i))
    return urllistPages
#Function to extract all the required elements from a product review page
def getReviews(soup, site, url):
    #for the filpkart website 
    if site == 'flipkart':
        #Extracting the Titles
        title_sec = soup.find_all("p",'_2-N8zT')
        title = []
        for s in title_sec:
            title.append(s.text)

        #Extracting the Author names
        author_sec = soup.find_all("p","_2sc7ZR _2V5EHH")
        author = []
        for r in author_sec:
            author.append(r.text)

        #Extracting the Text
        Review_text_sec = soup.find_all("div",'t-ZTKy')
        text = []
        for t in Review_text_sec:
            text.append(t.text)
            
        #Extracting the Star rating  
        Rating = soup.find_all("div", {"class": ["_3LWZlK _1BLPMq", "_3LWZlK _32lA32 _1BLPMq", "_3LWZlK _1rdVr6 _1BLPMq"]})    
        rate = []
        for d in Rating:
            rate.append(d.text)

        #Extracting the Date
        Date_sec = soup.find_all(lambda tag: tag.name == 'p' and tag.get('class') == ['_2sc7ZR'])    
        date = []
        for d in Date_sec:
          date.append(d.text)

        #Extracting the Helpful rating
        help_sec = soup.find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['_1LmwT9'])    
        help1 = []
        for d in help_sec:
          help1.append(d.text)
    #for the amazon website
    elif site == 'amazon':
        n_ = 0
        #Extracting the Titles
        title_sec = soup.find_all("a", attrs={'data-hook':"review-title"})
        title = []
        for s in title_sec:
            title.append(s.text.replace('\n', ''))
        n_ = len(title)

        #Extracting the Author names
        author_sec = soup.find_all("span", attrs ={"class": "a-profile-name"})
        author = []
        for r in author_sec:
            author.append(r.text)
        while(1):
            if len(author) > n_:
                author.pop(0)
            else:
                break

        #Extracting the Text
        Review_text_sec = soup.find_all("span", attrs={'data-hook': 'review-body'})
        text = []
        for t in Review_text_sec:
            text.append(t.text.replace('\n', ''))

        #Extracting the Star rating  
        Rating = soup.find_all("i", attrs={'data-hook': 'review-star-rating'})
        rate = []
        for d in Rating:
            rate.append(d.text)

        #Extracting the Date 
        Date_sec = soup.find_all("span",attrs={"data-hook": "review-date"})
        date = []
        for d in Date_sec:
          date.append(d.text) 

        #Extracting the Helpful rating 
        help_sec = soup.find_all("span", attrs={"data-hook": "helpful-vote-statement"})    
        help1 = []
        for d in help_sec:
             help1.append(d.text.replace('\n          ', '')) 
        while(1):
            if len(help1) < n_:
                help1.append(0)
            else:
                break
        
    #Adding the url of the first page of the review for reference  
    url1 = []
    url1 = [url] * len(date)

    #Creating a DataFrame for creating excel sheet
    collate = {'Date': date, 'URL': url1, 'Review_Title': title, 'Author': author, 'Rating': rate, 'text': text, 'Review_helpful': help1}          
    collate_df = pd.DataFrame.from_dict(collate)
    return collate_df
def scraper(url):
    df2 = []      
    soup = getsoup(url)
    site = url.split('.')[1]
    product = url.split('/')[3]
    lastPage = getLastPageNumber(soup, site)
    urllistPages = geturllist(url, lastPage)
    x = 1
    for url in urllistPages:
        soup = getsoup(url)
        df1 = getReviews(soup, site, url)         
        if x == 1:
            df3 = []
            df3 = df1
        else:                        
            df2 = df3
            result = pd.concat([df2,df1], ignore_index=True)
            df3 = result
        x += 1
    df3.to_csv(product + ".csv", index=False)


#flask framework working command for local host
app = Flask(__name__)


@app.route("/", methods =["GET", "POST"])
def home():
    return render_template('forntend.html')
@app.route("/about.html")
def about():
    return render_template('about.html')
@app.route("/contact.html")
def contact():
    return render_template('contact.html')

@app.route('/predict',methods=['POST'])
def predict():
    model = joblib.load('SGDClassifier.pkl')
    if request.method == "POST":
        url = request.form["link2"]
        product = url.split('/')[3]
        webscraping(url)
#remove_numbers function used for remove the numbers from reviews
    def remove_numbers(text):
        # define the pattern to keep
        pattern = r'[^a-zA-z.,!?/:;\"\'\s]' 
        return re.sub(pattern, '', text)
#remove_punctuation function used for removing comma, dot, !,?.
    def remove_punctuation(text):
        text = ''.join([c for c in text if c not in string.punctuation])
        return text
#remove_emoji function used for removing the emojis from reviews
    def remove_emoji(string):
        emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', string)

#used to remove white spaces or blank spaces
    def remove_extra_whitespace_tabs(text):
        #pattern = r'^\s+$|\s+$'
        pattern = r'^\s*|\s\s*'
        return re.sub(pattern, ' ', text).strip()
#used to splitting the text data within that column into individual units
    def tokenize(column):
    
        tokens = nltk.word_tokenize(column)
        return [w for w in tokens if w.isalpha()]
#remove Stopwords are frequently occurring words like "the," "a," "is," "in,"
    def remove_stopwords(tokenized_column):
        stops = set(stopwords.words("english"))
        return [word for word in tokenized_column if not word in stops]
#Stemming, in the context of pandas DataFrames, refers to the process of reducing words in a column to their root form
    def apply_stemming(tokenized_column):

    
        stemmer = PorterStemmer() 
        return [stemmer.stem(word).lower() for word in tokenized_column]
#used to concatenate a list of strings into a single string
    def rejoin_words(tokenized_column):
        return ( " ".join(tokenized_column))
#provide dataset to model and find the fake reviews and real reviews
    def prepare(product, model):
        global result
        df = pd.read_csv(product +".csv", names=['date', 'url', 'review_title','author','rating', 'text','review_helpful'])
        df.drop(0,axis=0,inplace=True)
        df['text'] = df['text'].str.replace('\n', ' ')
        df['text']=df['text'].apply(str)
        df['text'] = df.apply(lambda x: remove_numbers(x['text']), axis=1)
        df['text'] = df.apply(lambda x: remove_emoji(x['text']), axis=1)
        df['text'] = df.apply(lambda x: remove_punctuation(x['text']), axis=1)
        df['text'] = df.apply(lambda x: remove_extra_whitespace_tabs(x['text']), axis=1)
        df['tokenized'] = df.apply(lambda x: tokenize(x['text']), axis=1)
        df['stopwords_removed'] = df.apply(lambda x: remove_stopwords(x['tokenized']), axis=1)
        df['porter_stemmed'] = df.apply(lambda x: apply_stemming(x['stopwords_removed']), axis=1)
        df['all_text'] = df.apply(lambda x: rejoin_words(x['porter_stemmed']), axis=1)
        prediction = model.predict(df['all_text'])
        prediction=prediction.tolist()

        a=prediction.count(1)
        b=prediction.count(0)
        res1="The Count of Fake Reviews = {} ,".format(a)
        res2="The Count Of Real Reviews = {}".format(b)
        result=res1 + res2
    prepare(product,model)
    return render_template("forntend.html", pred=result)




if __name__ == '__main__':
    app.run(debug=True)
