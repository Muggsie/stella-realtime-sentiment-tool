# stella-realtime-sentiment-tool
A tool that reads and analyses tweets in realtime

# Introduction
Stella is an app that connects to Twitter's API for the purpose of reading tweets in realtime that contains keywords specified by the user and analyze tweets for their sentiment. It relies on the TextBlob library[TextBlob library](https://textblob.readthedocs.io/en/dev/)  for sentiment analysis. 
Some possible applications for this include:
* Calculating the social sentiment of particular political figures or issues
* Calculating sentiment scores for brands
* Using sentiment scores as training features for a learning algorithm to determine stock buy and sell triggers
* And more!

![visualizing data](https://i.ibb.co/S07hrWY/example.jpg)

# Requirements
You will need to obtain Twitter OAuth keys in order to connect to Twitter's API. Once you have them, go to the file 'credentials.py' and replace the *** with your own OAuth keys.[Click here](https://twittercommunity.com/t/how-to-get-my-api-key/7033) for instructions on how to obtain your keys.

Replace *** with your own keys:

```python
consumer_key = '*************************'
consumer_secret = '**************************************************'
access_token = '**************************************************'
access_token_secret = '*********************************************'
```

# Required libraries
	•	Tweepy (Twitter API)
	•	Textblob (Natural Language Processing)
	•	PyMongo (For working with MongoDB)
	•	Numpy (Computing averages, means etc)
	•	Datetime


