# !/usr/bin/env python
# encoding: utf-8

import tweepy # https://github.com/tweepy/tweepy
import csv
import json
import os
import sys
import datetime

# Configuration file
abs_path = os.path.dirname(os.path.realpath(__file__)) + '/'
with open("config_secret.json") as json_data_file:
    data = json.load(json_data_file)


# Twitter API credentials
consumer_key = data["consumer_key"]
consumer_secret = data["consumer_secret"]
access_key = data["access_key"]
access_secret = data["access_secret"]


def get_all_tweets(screen_name):
	print ("getting tweets from %s into csv file" % screen_name)
	# Twitter only allows access to a users most recent 3240 tweets with this method

	# authorize twitter, initialize tweepy
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth)

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
	outtweets = [[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in alltweets]

	# write the csv
	with open('%s_tweets.csv' % screen_name, 'wb') as f:
		writer = csv.writer(f)
		writer.writerow(["id", "created_at", "text"])
		writer.writerows(outtweets)

	pass


def getSeconds(time_str):
	h, m, s = time_str.split(':')
	return int(h)*3600 + int(m)*60 + int(s)


def averageTweetTime(screen_name):
	with open(screen_name+'_tweets.csv') as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		dates = []
		for row in readCSV:
			date = row[1]
			dates.append(date)
		# print(dates)
		total = 0
		for date in dates:
			# print(date[11: len(date)])
			if(date != "created_at"): # skip first line
				# print(getSeconds(date[11: len(date)]))
				total += getSeconds(date[11: len(date)])
		averageseconds = total/(len(dates)-1) # don't count the first line
		average24HrFormat = str(datetime.timedelta(seconds=averageseconds))
		print("average tweet time is: %s" % average24HrFormat)


if __name__ == '__main__':
	# pass in the username of the account you want to download
	get_all_tweets(sys.argv[1])
	averageTweetTime(sys.argv[1])
