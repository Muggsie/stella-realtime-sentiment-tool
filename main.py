import re, json, time, datetime, logging, urllib3
from tweepy.streaming import StreamListener
from tweepy import Stream, OAuthHandler
from bson.objectid import ObjectId
from pymongo import MongoClient
from textblob import TextBlob
from credentials import *
import numpy as np
import tweepy

"""
Stella is an app that connects to Twitter's API for the purpose of reading
tweets in realtime that contains keywords specified by the user and analyze 
their sentiment. Data is written to mongodb.
"""

# init the interface to our db
connect = MongoClient('localhost', 27017) # this assumes you are running a MongoDB at localhost on port 27017 
db = connect.stella.sentiment # creates a db named stella and a collection names sentiment

# how often we write to our db (in seconds) 
write_frequency = 60 

twitter_keywords_to_track = [
    'bitcoin',
    'btc'
]

def calctime(a):
    return time.time()-a

average = 0
total_volume = 0 
very_positive_volume = 0
positive_volume = 0
neutral_volume = 0
negative_volume = 0
very_negative_volume = 0

# initializing time to create the timeseries
initime = time.time() 

# logging exceptions
logging.INFO
LOG = logging.getLogger(__name__)

print('Stella is initializing.... ')
print(f'Will compute sentiment for Tweets that mention either one of these keywords {twitter_keywords_to_track}')

class listener(StreamListener):

    def on_data(self, data):
        global initime
        # t = int(calctime(initime)) 
        all_data = json.loads(data)
        tweet = all_data["text"].strip()
        tweet = " ".join(re.findall("[a-zA-Z]+", tweet)) # locating only text
        blob = TextBlob(tweet.strip()) # cleaning unwanted stuff from tweet

        # we use global variables to temporarily store data before writing to our db
        global total_volume
        global average
        global very_positive_volume
        global positive_volume
        global neutral_volume
        global negative_volume
        global very_negative_volume

        total_volume = total_volume + 1
        senti = 0
        sentiment = []

        # here you can modify the values for the sentiment logic
        for sen in blob.sentences:
            senti = senti + sen.sentiment.polarity
            
            if sen.sentiment.polarity > 0.6:
                very_positive_volume += 1

            elif sen.sentiment.polarity < -0.6:
                very_negative_volume += 1

            elif sen.sentiment.polarity > 0.25:
                positive_volume += 1
            
            elif sen.sentiment.polarity < -0.25:
                negative_volume += 1

            else:
                neutral_volume += 1
                
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
twitterStream = Stream(auth, listener(total_volume))

# this section catches exceptions and restarts our listener
def start_stream(stream, **kwargs):
    while True:
        try:
            stream.filter(**kwargs)
            break
            
        except urllib3.exceptions.ReadTimeoutError:
            stream.disconnect()
            LOG.exception("ReadTimeoutError exception")
            time.sleep(5)
            start_stream(stream, **kwargs)

        except urllib3.exceptions.IncompleteRead:
            stream.disconnect()
            LOG.exception("Cut off due to app consumes data slower than it is produced")
            time.sleep(5)
            start_stream(stream, **kwargs)

# initializing the stream
start_stream(twitterStream, track = twitter_keywords_to_track, is_async=True)

while True:

    time.sleep(write_frequency)
    now = datetime.datetime.utcnow()

    # prints aggregated data to terminal
    print(f'{now} Total:{total_volume} Sentiment:{average} +Pos:{very_positive_volume} Pos:{positive_volume} Neu:{neutral_volume} Neg:{negative_volume} +Neg:{very_negative_volume}')

    # preparing aggregated data in dict before insterting to db 
    entry = {
        '_id': str(ObjectId()),
        'coin':'bitcoin',
        'time': now,
        'sentiment': average,
        'volume': total_volume,
        'very_positve': very_positive_volume,
        'positive': positive_volume,
        'neutral': neutral_volume,
        'negative': negative_volume,
        'very_negative': very_negative_volume
    }

    # inserting our dict to db
    db.insert_one(entry)

    # Reset aggregated data in global variables
    total_volume = 0 
    average = 0
    very_positive_volume = 0
    positive_volume = 0
    neutral_volume = 0
    negative_volume = 0
    very_negative_volume = 0 
