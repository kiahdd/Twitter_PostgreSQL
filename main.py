
import key as c
import tweepy
import sqlalchemy 
from pprint import pprint
from textblob import TextBlob
from nltk.corpus import stopwords
import re

from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert


# constants
consumer_key            = c.API_KEY
consumer_secret         = c.API_KEy_SECRET
access_token            = c.Access_token
access_token_secret     = c.Access_token_secret
tweetsPerQry            = 100
maxTweets               = 1000
hashtag                 = c.hashtag

# Data processing: Cleaning Tweet texts
def clean_text(new_tweet):
    ex_list = ['rt', 'http[^\s]*', 'RT', '#[^\s]*\S', '@[^\s]*:\S']
    exc = '|'.join(ex_list)
    text = re.sub(exc, '' , new_tweet)
    text = text.lower()
    words = text.split()
    stopword_list = stopwords.words('english')
    words = [word for word in words if not word in stopword_list]
    clean_text = ' '.join(words)
    return clean_text


def sentiment_score(new_tweet):
    analysis = TextBlob(new_tweet)
    if analysis.sentiment.polarity > 0:
        return 1 #positive
    elif analysis.sentiment.polarity == 0: #neutrial
        return 0
    else:
        return -1  #negative

def get_engine():
    pass

def main():
    """
    This function first query twitter to download data
    Then insert results into a postgreSQL local server
    """
    # Authenticate to Twitter
    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
    api  = tweepy.API(auth)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    # Get the User object for twitter...
    maxId = -1  # initialization
    tweetCount = 0
    meta_list = []
    
    while tweetCount< maxTweets:
        newTweets = []

        if(maxId <= 0): # reteriving the most recent tweets
            print("Retrieving  the most recent tweets ...")
            newTweets = api.search_tweets(q=hashtag,count=tweetsPerQry, result_type="recent",tweet_mode="extended")
        else:  
            print("Retrieving older tweets ...")
            # Returns only statuses with an ID less than (that is, older than) or equal to the specified ID
            newTweets = api.search_tweets(q=hashtag, count=tweetsPerQry, max_id=str(maxId - 1), result_type="recent", tweet_mode="extended")

        if not newTweets:
            print("Done!")
            break

        for tweet in newTweets:
            username = tweet.user.name  #username
            created_at = str(tweet.created_at)  # when it was posted?

            #obtain full tex for retweets and tweets
            try:
                tweet_text = tweet.retweeted_status.full_text   # full text of retweet
                continue   # if it was a retweet skip

            except AttributeError:  # Not a Retweet
                tweet_text = tweet.full_text # full text of tweet

            tweet_text_sent = tweet_text    
            retweet_count = tweet.retweet_count  
            fav_count = tweet.favorite_count
            media_source = tweet.source

            # cleaning tweet text to remove hashtages
            tweet_text_sent = clean_text(tweet_text_sent)

            # sentiment score analysis
            result_score = sentiment_score(tweet_text_sent)

            #convert to dic
            data_dict = {
            "username":username,
            "created_at":created_at,
            "tweet_text":tweet_text_sent,
            "retweet_count":retweet_count,
            "fav_count":fav_count,
            "media_source":media_source,
            "sentiment_score":result_score
            }
            # print(data_dict["sentiment_score"])
            meta_list.append(data_dict)
        # end for
        tweetCount += len(newTweets)
        maxId = newTweets[-1].id

    engine = create_engine(c.postgre_url)
    conn = engine.connect()
    metadata = MetaData()
    print("printing meta data ...")
    
   
    # reflect db schema to MetaData
    trans = conn.begin()
    metadata.reflect(bind=engine,schema=c._schema)
    print(metadata.tables)
    
    table_name = metadata.tables[c.table_name]

    insert_stmt = insert(table_name)
    #if you have constraint in your database, and you just want to update unique record
    # do_nothing_stmt = insert_stmt.on_conflict_do_nothing(constraint='')
    result_proxy = conn.execute(insert_stmt, meta_list)
    trans.commit() 
    conn.close()

# print(clean_text("#ukrain is hoding againse #nuclear fd"))
main()


