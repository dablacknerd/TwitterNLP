import time
import tweepy
import pandas as pd
import json
from datetime import datetime

def file_names(query):
    time_str = "{}-{}-{}-{}-{}-{}".format(datetime.now().month, datetime.now().day, datetime.now().year,datetime.now().hour,datetime.now().minute, datetime.now().second)
    if query.startswith("#"):
        filename = query[1:]
    else:
        filename = query
    
    return{"tweets":filename + "-Tweets-" + time_str + ".csv",
           "user_mentions":filename + "-User-Mentions-" + time_str + ".csv",
           "hash_tags":filename + "-Hashtags-" + time_str + ".csv"
          }
def extract_hashtags(entities_dict):
    if type(entities_dict) == str:
        entities_dict = json.loads(entities_dict.replace("\'", "\""))

    hashtags = []
    if len(entities_dict['hashtags']) > 0:
        counter = 1
        for row in entities_dict['hashtags']:
            hashtags.append([counter, row['text']])
            counter += 1
        return hashtags
    else:
        return None

def extract_user_mentions(usermention_dict):
    if type(usermention_dict) == str:
        usermention_dict = json.loads(usermention_dict.replace("\'", "\""))
    
    user_mentions =[]
    if len(usermention_dict['user_mentions']) > 0:
        counter = 1
        for row in usermention_dict['user_mentions']:
            user_mentions.append([counter, row['id'], row['screen_name'], row['name']])
            counter += 1
        return user_mentions
    else:
        return None

def limit_handled(cursor):
    flag = True
    while flag:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15 * 60)
        except StopIteration:
            print("==========================")
            print("Done!")
            flag = False

def pull_from_twitter1(tweepy_cursor_object):
    container = []
    cols = ["tweet_id", "created_at", "author", "text", "source", "is_truncated", "entities","retweet_count","favorite_count","language"]
    for status in tweepy_cursor_object:
        created_at = status.created_at
        tweet_id = status.id
        try:
            full_text = status.retweeted_status.full_text
        except AttributeError:
            full_text = status.full_text
        truncated = status.truncated
        entities = status.entities
        source = status.source
        user = status.user.screen_name
        retweet_count = status.retweet_count
        favorite_count = status.favorite_count
        language = status.lang
        row = [tweet_id, created_at, user, full_text, source, truncated, entities, retweet_count, favorite_count, language]
        container.append(row)
    return pd.DataFrame(container,columns=cols)

def pull_from_twitter2(status_collection):
    container = []
    cols = ["tweet_id", "created_at", "author", "text", "source", "is_truncated", "entities","retweet_count","favorite_count","language"]
    for status in status_collection:
        created_at = status.created_at
        tweet_id = status.id
        try:
            full_text = status.retweeted_status.full_text
        except AttributeError:
            full_text = status.full_text
        truncated = status.truncated
        entities = status.entities
        source = status.source
        user = status.user.screen_name
        retweet_count = status.retweet_count
        favorite_count = status.favorite_count
        language = status.lang
        row = [tweet_id, created_at, user, full_text, source, truncated, entities, retweet_count, favorite_count, language]
        container.append(row)
    return pd.DataFrame(container,columns=cols)

def process_tweets(status):
    hash_tags =[]
    user_mentions=[]
    created_at = status.created_at
    tweet_id = status.id
    try:
        full_text = status.retweeted_status.full_text
    except AttributeError:
        full_text = status.full_text
    truncated = status.truncated
    source = status.source
    user = status.user.screen_name
    retweet_count = status.retweet_count
    favorite_count = status.favorite_count
    language = status.lang
    row = [tweet_id, created_at, user, full_text, source, truncated, retweet_count, favorite_count, language]
    if extract_hashtags(status.entities):
        for hash_tag_row in extract_hashtags(status.entities):
            hash_tags.append([tweet_id, hash_tag_row[0], hash_tag_row[1]])
    
    if extract_user_mentions(status.entities):
        for user_mention_row in extract_user_mentions(status.entities):
            user_mentions.append([tweet_id, user_mention_row[0],user_mention_row[1], user_mention_row[2], user_mention_row[3]])
    return {"tweet":row, "hashtags":hash_tags, "usermentions":user_mentions}