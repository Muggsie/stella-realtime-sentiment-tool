from tweepy.streaming import StreamListener
from textblob import TextBlob
from tweepy import Stream
from tweepy import OAuthHandler
import matplotlib.pyplot as plt
import re, json, time, numpy
import tweepy

"""
this app reads tweets that contains specified keywords and analyze their sentiment. 
It also categorizes tweets based on sentiment value and count them

future implementations
 - compute standard deviation + z-score for each dataset
 - implement __init__
 - add new visualisation style
 - add database
"""

# replace *** with your own access tokens and secret keys. You need to create an account at https://developer.twitter.com/ and obtain them here
consumer_key = '********************************'
consumer_secret = '********************************'
access_token = '********************************'
access_token_secret = '********************************'

track_this = [
    'bitcoin',
    'btc'
]

def calctime(a):
    return time.time()-a

# we are counting tweets based on their sentiment category
positive = 0
negative = 0
compound = 0
average = 0
mean = 0

count = 0 
very_positive_tweet_count = 0
positive_tweet_count = 0
neutral_tweet_count = 0
negative_tweet_count = 0
very_negative_tweet_count = 0

initime = time.time() # initializing time to create the timeseries
plt.ion() # for an interactive chart

class listener(StreamListener):

    def on_data(self, data):
        global initime
        t = int(calctime(initime))
        all_data = json.loads(data)
        tweet = all_data["text"].strip()
        tweet = " ".join(re.findall("[a-zA-Z]+", tweet)) # locating only text
        blob = TextBlob(tweet.strip()) # cleaning unwanted stuff from tweet

        global positive
        global negative
        global compound
        global average
        global mean
        
        global count
        global very_positive_tweet_count
        global positive_tweet_count
        global neutral_tweet_count
        global negative_tweet_count
        global very_negative_tweet_count

        count = count + 1
        senti = 0
        sentiment = []

        for sen in blob.sentences:
            senti = senti + sen.sentiment.polarity
            
            if sen.sentiment.polarity <= -0.5:
                very_negative_tweet_count += 1

            elif sen.sentiment.polarity >= 0.5:
                very_positive_tweet_count += 1

            elif sen.sentiment.polarity > 0:
                positive_tweet_count += 1
            
            elif sen.sentiment.polarity < 0:
                negative_tweet_count += 1

            else:
                neutral_tweet_count += 1
                
            sentiment.append(senti)
            
        compound = compound + senti
        #average = numpy.mean(sentiment)

        # print results to terminal
        print(count)
        print(tweet.strip())
        print(senti)
        print(t)
        print(f'VP: {very_positive_tweet_count} P: {positive_tweet_count} Neutral: {neutral_tweet_count} N: {negative_tweet_count} VN: {very_negative_tweet_count}')
        print(' ')

        # for plotting our chart
        plt.axis([0, 200, -20, 20])
        plt.xlabel('Time')
        plt.ylabel('Sentiment')
        plt.plot([t], [positive], 'go', [t], [negative], 'ro', [t], [compound], 'bo')
        plt.show()

        # breaks the program when it has processed tweet number 200
        plt.pause(0.0001)
        if count == 600:
            return False
        else:
            return True

    # print error messages to terminal
    def on_error(self, status):
        print(status)

# feeding our twitter api access tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# initilizing the listener 
twitterStream = Stream(auth, listener(count))
twitterStream.filter(track = track_this)
