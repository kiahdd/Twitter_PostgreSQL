#%%
import key as c
import tweepy
import sqlalchemy 
from pprint import pprint
from textblob import TextBlob
from nltk.corpus import stopwords
import re
import sys

# constants
consumer_key            = c.API_KEY
consumer_secret         = c.API_KEy_SECRET
access_token            = c.Access_token
access_token_secret     = c.Access_token_secret
tweetsPerQry            = 1
maxTweets               = 100000
hashtag                 = "#InternetShutDown"

# Data processing: Cleaning Tweet texts
def clean_text(new_tweet):
    ex_list = ['rt', 'http', 'RT', '#.*\S', '@.*:\S']
    exc = '|'.join(ex_list)
    text = re.sub(exc, '' , new_tweet)
    text = text.lower()
    words = text.split()
    stopword_list = stopwords.words('english')
    words = [word for word in words if not word in stopword_list]
    clean_text = ' '.join(words)
    return clean_text


def sentiment_score(new_tweet):
    pass


def main():
    """
    This function first query twitter to download data
    """
    # Authenticate to Twitter
    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
    api  = tweepy.API(auth)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    # Get the User object for twitter...
    maxId = -1
    tweetCount = 0
    meta_list = []

    if(maxId <= 0):
        newtweets = api.search_tweets(q=hashtag,count=tweetsPerQry, result_type="recent",tweet_mode="extended")
    else: 
        newTweets = api.search(q=hashtag, count=tweetsPerQry, max_id=str(maxId - 1), result_type="recent", tweet_mode="extended")

    if not newTweets:
        print("Done")
        sys.exit(0)
    for tweet in newtweets:
        username = tweet.user.name
        created_at = str(tweet.created_at)

        try:
            tweet_text = tweet.retweeted_status.full_text
        except AttributeError:  # Not a Retweet
            tweet_text = tweet.full_text
        tweet_text = tweet.retweeted_status.full_text
        tweet_text_sent = tweet_text
        retweet_count = tweet.retweet_count
        fav_count = tweet.favorite_count
        media_source = tweet.source
        tweet_text_sent = clean_text(tweet_text_sent)
        print(tweet_text)
        pprint(tweet_text_sent)
        print(retweet_count)
        print(media_source)
# main()



# %%
