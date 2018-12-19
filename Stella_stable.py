import re, json, time, datetime, logging, urllib3
from tweepy.streaming import StreamListener
from textblob import TextBlob
from tweepy import Stream
from tweepy import OAuthHandler
from pymongo import MongoClient
import numpy as np
import tweepy

"""
Stella is an app that connects to Twitter's API for the purpose of reading
tweets in realtime that contains keywords specified by the user and analyze 
their sentiment 

we use a mongodb to store our data

future implementations
 - compute standard deviation + z-score for each dataset
 - improve error handling
 - weight tweet importance by user (ie. more followers = more weight)
 - add data visualization
"""

# init the interface to our db
connect = MongoClient('localhost', 27017) # this assumes you are running a MongoDB at localhost on port 27017 
db = connect.stella.sentiment # 'stella' is the database name and 'sentiment' is the collection name. You can change this to whatever you like

# how often we write to our db (in seconds) 
write_frequency = 60 

# specify the keywords you want to track
track_this = [
    'bitcoin',
    'btc'
]

# You need to create an account at https://developer.twitter.com/ 
# and get your personal access tokens and secret keys
# replace *** with your own 
consumer_key = '********************************'
consumer_secret = '********************************'
access_token = '********************************'
access_token_secret = '********************************'

def calctime(a):
    return time.time()-a

average = 0
count = 0 
very_positive_count = 0
positive_count = 0
neutral_count = 0
negative_count = 0
very_negative_count = 0

initime = time.time() # initializing time to create the timeseries

# logging exceptions
logging.INFO
LOG = logging.getLogger(__name__)

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
        global very_positive_count
        global positive_count
        global neutral_count
        global negative_count
        global very_negative_count

        count = count + 1
        senti = 0
        sentiment = []

        # here you can modify the values for the sentiment logic
        for sen in blob.sentences:
            senti = senti + sen.sentiment.polarity
            
            if sen.sentiment.polarity > 0.6:
                very_positive_count += 1

            elif sen.sentiment.polarity < -0.6:
                very_negative_count += 1

            elif sen.sentiment.polarity > 0.25:
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

# this section catches exceptions and restarts our listener
def start_stream(stream, **kwargs):
    while True:
        try:
            stream.filter(**kwargs)
            break
            
        except urllib3.Response.ReadTimeoutError:
            stream.disconnect()
            LOG.exception("ReadTimeoutError exception")
            start_stream(stream, **kwargs)
            
        except urllib3.Response.SocketError:
            stream.disconnect()
            LOG.exception("Fatal exception. Consult logs.")
            start_stream(stream, **kwargs)

        except urllib3.Response.IncompleteRead:
            stream.disconnect()
            LOG.exception("Cut off due to app consumes data slower than it is produced")
            start_stream(stream, **kwargs)

start_stream(twitterStream, track = track_this, is_async=True)

while True:

    time.sleep(write_frequency)
    now = datetime.datetime.now().isoformat()

    # prints aggregated data to terminal
    print(f'{now} Total:{count} Sentiment:{average} +Pos:{very_positive_count} Pos:{positive_count} Neu:{neutral_count} Neg:{negative_count} +Neg:{very_negative_count}')

    # preparing aggregated data in dict before insterting to db 
    entry = {
        'coin':'bitcoin',
        'time':now,
        'sentiment':average,
        'volume':count,
        'very_positve':very_positive_count,
        'positive':positive_count,
        'neutral':neutral_count,
        'negative':negative_count,
        'very_negative':very_negative_count
    }

    # inserting our dict to db
    db.insert_one(entry)

    # Reset aggregated data in global variables
    count = 0 
    average = 0
    very_positive_count = 0
    positive_count = 0
    neutral_count = 0
    negative_count = 0
    very_negative_count = 0 
