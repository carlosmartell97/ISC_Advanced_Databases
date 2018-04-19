# !/usr/bin/env python
# encoding: utf-8

import tweepy  # https://github.com/tweepy/tweepy
import csv
import json
import os
import sys
import datetime
from kivy_window import Twitter_AnalysisApp
from unidecode import unidecode
import Global
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import itertools

# Configuration file
abs_path = os.path.dirname(os.path.realpath(__file__)) + '/'
with open("config_secret.json") as json_data_file:
    data = json.load(json_data_file)


# Twitter API credentials
CONSUMER_KEY = data["consumer_key"]
CONSUMER_SECRET = data["consumer_secret"]
ACCESS_KEY = data["access_key"]
ACCESS_SECRET = data["access_secret"]

# authorize twitter, initialize tweepy
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)


def get_all_tweets(screen_name):
    # Twitter only allows access to a users most recent 3240 tweets with this method

    print ("getting all tweets from %s into csv file..." % screen_name)
    # initialize a list to hold all the tweepy Tweets
    alltweets = []
    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=screen_name, count=200)
    # save most recent tweets
    alltweets.extend(new_tweets)
    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1
    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        # print "getting tweets before %s" % (oldest)

        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name=screen_name, count=200, max_id=oldest)
        # save most recent tweets
        alltweets.extend(new_tweets)
        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        # print "...%s tweets downloaded so far" % (len(alltweets))

    # transform the tweepy tweets into a 2D array that will populate the csv
    outtweets = [[tweet.id_str, tweet.created_at, tweet.retweet_count, tweet.favorite_count, tweet.text.encode("utf-8")] for tweet in alltweets]

    # write the csv
    with open("csv/"+'%s_tweets.csv' % screen_name, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "created_at", "retweets", "favorites", "text"])
        writer.writerows(outtweets)
    pass


def getSeconds(time_str):
    h, m, s = time_str.split(':')
    return int(h)*3600 + int(m)*60 + int(s)


def averages(screen_name):
    with open("csv/"+screen_name+'_tweets.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        rows = 0
        totalTime = 0
        totalRetweets = 0
        totalFavorites = 0
        tweets_file = open("txt/"+screen_name+"_tweets_only.txt", "w")
        tweets_same_day = 1
        most_tweets_per_day = 0
        most_tweets_day = ""
        previous_tweet_date = ""
        date_str = ""
        for row in readCSV:
            rows += 1
            date = row[1]
            retweets = row[2]
            favorites = row[3]
            tweetText = row[4]
            tweets_file.write(tweetText+"\n\n")
            if(date != "created_at"):  # skip first line
                totalTime += getSeconds(date[11: len(date)])
                date_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                date_str = str(date_obj.year)+"-"+str(date_obj.month)+"-"+str(date_obj.day)
                # print(" date_str: %s" % date_str)
                if(date_str == previous_tweet_date):
                    tweets_same_day += 1
                    if(tweets_same_day > most_tweets_per_day):
                        most_tweets_per_day = tweets_same_day
                        most_tweets_day = date_str
                else:
                    tweets_same_day = 1
                # print("  on %s, \t%d tweets" % (date_str, tweets_same_day))
            previous_tweet_date = date_str
            if(retweets != "retweets"):  # skip first line
                totalRetweets += int(retweets)
            if(favorites != "favorites"):  # skip first line
                totalFavorites += int(favorites)
        tweets_file.close()
        generate_word_cloud(screen_name)
        numTweets = rows - 1
        if(numTweets >= 1):
            readCSV = csv.reader(open("csv/"+screen_name+'_tweets.csv'), delimiter=',')
            row_1 = next(itertools.islice(readCSV, numTweets, numTweets+1))
            print(" 1st tweet: %s" % row_1[4])
            first_tweet_date = datetime.datetime.strptime(row_1[1], "%Y-%m-%d %H:%M:%S")
            account_created_date = datetime.datetime.strptime(Global.created_at, "%Y-%m-%d %H:%M:%S")
            date_delta = first_tweet_date - account_created_date
            print("1st tweet date: %s" % first_tweet_date)
            print("account created date: %s" % account_created_date)
            print("time taken to make 1st tweet: %s DAYS %s SECONDS" % (str(date_delta.days), str(date_delta.seconds)))
            Global.time_taken_1st_tweet = "%s DAYS %s SECONDS" % (str(date_delta.days), str(date_delta.seconds))
        if(numTweets >= 100):
            readCSV = csv.reader(open("csv/"+screen_name+'_tweets.csv'), delimiter=',')
            row_100 = next(itertools.islice(readCSV, numTweets-100, numTweets-99))
            print(" 100th tweet: %s" % row_100[4])
            tweet_100_date = datetime.datetime.strptime(row_100[1], "%Y-%m-%d %H:%M:%S")
            date_delta = tweet_100_date - first_tweet_date
            print("100th tweet date: %s" % tweet_100_date)
            print("1st tweet date date: %s" % first_tweet_date)
            print("from then, time taken to make 100 tweets: %s DAYS %s SECONDS" % (str(date_delta.days), str(date_delta.seconds)))
            Global.time_taken_100_tweets = "%s DAYS %s SECONDS" % (str(date_delta.days), str(date_delta.seconds))
        averageSeconds = totalTime/numTweets  # don't count the first line
        average24HrFormat = str(datetime.timedelta(seconds=averageSeconds))
        averageRetweets = totalRetweets/(numTweets)  # don't count the first line
        averageFavorites = totalFavorites/(numTweets)  # don't count the first line
        Global.tweets = str(numTweets) + "\ntweets"
        Global.average_tweet_time = average24HrFormat + "\naverage tweet time"
        Global.average_tweet_retweets = str(averageRetweets) + "\naverage retweets in tweets"
        Global.average_tweet_favorites = str(averageFavorites) + "\naverage favorites in tweets"
        Global.most_tweets_per_day = most_tweets_per_day
        Global.most_tweets_day = most_tweets_day
        print("total amount of tweets: %s" % numTweets)
        print("average tweet time is: %s" % average24HrFormat)
        print("average retweets in tweets: %s" % averageRetweets)
        print("average favorites in tweets: %s" % averageFavorites)


def handle_limit(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            # time.sleep(15 * 60)  # wait encouraged 15 minutes
            print "Rate limit reached!"
            break


def get_user_info(screen_name):
    # get user's info
    user = api.get_user(screen_name)
    screen_name = user.screen_name
    description = user.description
    followers = user.followers_count
    following = user.friends_count
    profile_image_url = user.profile_image_url.replace("normal", "200x200")
    location = user.location
    verified = user.verified
    created_at = user.created_at

    # app = App.get_running_app()
    Global.image_url = profile_image_url
    Global.screen_name = "@" + screen_name
    if(description != ""):
        Global.description = description
    if(location != ""):
        Global.location = "location: " + unidecode(location)
    Global.verified = "verified: " + str(verified)
    Global.created_at = str(created_at)
    Global.followers = str(followers) + "\nfollowers"
    Global.following = str(following) + "\nfollowing"

    print("screen name: %s" % screen_name)
    print("created at: %s" % created_at)
    print("followers: %s" % followers)
    print("following: %s" % following)
    print("image url: %s" % profile_image_url)
    print("location: %s" % location)
    print("verified: %s" % verified)

    print("examining %s's followers..." % screen_name)
    # get followback percentage
    MAX_RETRIEVE_FOLLOWERS = 50
    num_follower = 0
    followback_total = 0
    for follower in handle_limit(tweepy.Cursor(api.followers, screen_name=screen_name, count=MAX_RETRIEVE_FOLLOWERS).items()):
        num_follower += 1
        if(num_follower > MAX_RETRIEVE_FOLLOWERS):
            break
        # print "followed by: #%d %s" % (num_follower, follower.screen_name)
        if api.show_friendship(source_screen_name=screen_name, target_screen_name=follower.screen_name)[0].following:  # user follows back this follower
            # print "%s follows %s back!" % (screen_name, follower.screen_name)
            followback_total += 1
    # print("total follows back: %d     followers: %d     num_follower: %d" % (followback_total, followers, num_follower))
    if followers == MAX_RETRIEVE_FOLLOWERS or followers < MAX_RETRIEVE_FOLLOWERS:
        followback_percentage = (followback_total*100)/followers
        Global.followback_percentage = "from all of %s's %d followers, %d have been followed back, %d%% of them" % (screen_name, followers, followback_total, followback_percentage)
        print("from all of %s's %d followers, %d have been followed back, %d%% of them" % (screen_name, followers, followback_total, followback_percentage))
    else:  # only the newest followers will were examined, to avoid reaching the API's rate limit
        followback_percentage = (followback_total*100)/MAX_RETRIEVE_FOLLOWERS
        Global.followback_percentage = "from %s's newest %d followers, %d have been followed back, %d%% of them" % (screen_name, MAX_RETRIEVE_FOLLOWERS, followback_total, followback_percentage)
        print("from %s's newest %d followers, %d have been followed back, %d%% of them" % (screen_name, MAX_RETRIEVE_FOLLOWERS, followback_total, followback_percentage))


def generate_word_cloud(screen_name):
    d = os.path.dirname(__file__)

    # Read the whole text.
    tweetsText = open(os.path.join(d, "txt/"+screen_name+"_tweets_only.txt")).read()

    wordcloud = WordCloud(max_font_size=40).generate(tweetsText)
    figure = plt.figure(dpi=300)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    # plt.show()
    figure.savefig("png/"+screen_name+"_word_cloud.png", bbox_inches='tight', transparent=True, pad_inches=0, dpi=300)
    Global.wordcloud_image = "png/"+screen_name+"_word_cloud.png"


if __name__ == '__main__':
    # pass in the username of the account you want to analyze
    get_all_tweets(sys.argv[1])
    get_user_info(sys.argv[1])
    averages(sys.argv[1])
    Twitter_AnalysisApp().run()
