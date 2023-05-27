import tweepy
from textblob import TextBlob
import re
import json

class TwitterClient(object):
    def __init__(self):
        consumer_key = 'YourTwitterAPIKey'
        consumer_secret = 'YourTwitterAPISecretKey'
        access_token = 'YourTwitterAccessToken'
        access_token_secret = 'YourTwitterAccessTokenSecret'
        
        try:
            self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            self.auth.set_access_token(access_token, access_token_secret)
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")
            
    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
    
    def get_tweet_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'
            
    def get_tweets(self, query, count=10):
        tweets = []
        
        try:
            fetched_tweets = self.api.search(q=query, count=count, lang="en", tweet_mode='extended')
            
            for tweet in fetched_tweets:
                parsed_tweet = {}
                if 'retweeted_status' in tweet._json:
                    parsed_tweet['text'] = tweet.retweeted_status.full_text
                else:
                    parsed_tweet['text'] = tweet.full_text
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.full_text)
                if tweet.geo:
                    parsed_tweet['location'] = tweet.geo
                elif tweet.user.location:
                    parsed_tweet['location'] = tweet.user.location
                
                if tweet.retweet_count > 0:
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)
            
            return tweets
        
        except tweepy.TweepError as e:
            print("Error : " + str(e))
            
def main():
    api = TwitterClient()
    disaster_keywords = ['earthquake', 'flood', 'hurricane', 'wildfire', 'tsunami', 
                         'tornado', 'avalanche', 'landslide', 'drought', 'storm', 'volcano', 
                         'blizzard', 'cyclone', 'typhoon']

    all_disaster_tweets = []
    for keyword in disaster_keywords:
        tweets = api.get_tweets(query=keyword, count=200)
        all_disaster_tweets.extend(tweets)

    all_disaster_tweets.sort(key=lambda x: x.get('location', None))

    with open('disaster_tweets.json', 'w') as f:
        json.dump(all_disaster_tweets, f)

if __name__ == "__main__":
    main()
