from sqlalchemy import Table, Column, String, MetaData
from sqlalchemy import create_engine
from tweepy.streaming import StreamListener
from textblob import TextBlob
from tweepy import Stream
from tweepy import OAuthHandler
import re, json, time, datetime
import numpy as np
import tweepy

"""
Stella is an app that connects to Twitter's API for the purpose of reading
tweets that contains keywords specified by the user and analyze their sentiment 
sentiment results are stored in a postgres db

future implementations
 - compute standard deviation + z-score for each dataset
 - improve error handling
 - weight tweet importance by user (more followers = more weight)
 - add data visualization
"""

# init the interface to our db
# this assumes you have a postgres db at your disposal. 
db_string = "postgres://USER:PASSWORD@HOST:PORT/postgres" # replace capitalized words with your own details
db = create_engine(db_string)

# replace *** with your own access tokens and secret keys. You need to create an account at https://developer.twitter.com/ and obtain them here
consumer_key = '********************************'
consumer_secret = '********************************'
access_token = '********************************'
access_token_secret = '********************************'

# specify the keywords you want to track
track_this = [
    'bitcoin',
    'btc'
]

# how often we write to our db (in seconds) 
read_frequency = 60 

def calctime(a):
    return time.time()-a

# we are counting and computing sentiment averages
count = 0 
average = 0
positive_count = 0
neutral_count = 0
negative_count = 0

initime = time.time() # initializing time to create the timeseries

class listener(StreamListener):

    def on_data(self, data):
        global initime
        # t = int(calctime(initime)) 
        all_data = json.loads(data)
        tweet = all_data["text"].strip()
        tweet = " ".join(re.findall("[a-zA-Z]+", tweet)) # locating only text
        blob = TextBlob(tweet.strip()) # cleaning unwanted stuff from tweet

        # we use global variables to temporarily store data before writing to our db
        global count
        global average
        global positive_count
        global neutral_count
        global negative_count

        count = count + 1
        senti = 0
        sentiment = []

        # here you can modify the values for the sentiment logic
        for sen in blob.sentences:
            senti = senti + sen.sentiment.polarity
            
            if sen.sentiment.polarity > 0.25:
                positive_count += 1
            
            elif sen.sentiment.polarity < -0.25:
                negative_count += 1

            else:
                neutral_count += 1
                
            sentiment.append(senti)
        
        # we use numpy to compute average values. Will add computation for std deviations and z-values later on
        average = np.average(senti)

    # print error messages to terminal
    def on_error(self, status):
        print(status)

# feeding our twitter api access tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# initilizing the listener 
twitterStream = Stream(auth, listener(count))
twitterStream.filter(track = track_this, is_async=True)

while True:

    time.sleep(read_frequency)
    now = datetime.datetime.now().isoformat()

    # prints aggregated data to terminal
    print(f'{now} Total: {count} Sentiment: {average} Positive #: {positive_count} Neutral #: {neutral_count} Negative #: {negative_count}')

    # writes aggregated data to our db
    db.execute("INSERT INTO bitcoin (time, sentiment, volume, positive, neutral, negative) VALUES (%s, %s, %s, %s, %s, %s)", (now, average, count, positive_count, neutral_count, negative_count))

    # Reset aggregated data in global variables
    count = 0 
    average = 0
    positive_count = 0
    neutral_count = 0
    negative_count = 0
