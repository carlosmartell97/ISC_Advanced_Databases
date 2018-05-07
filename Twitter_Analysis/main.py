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
import re
from py2neo import Graph, authenticate, Path

# Configuration file
abs_path = os.path.dirname(os.path.realpath(__file__)) + '/'
with open("config_secret.json") as json_data_file:
    data = json.load(json_data_file)


# Twitter API credentials
CONSUMER_KEY = data["consumer_key"]
CONSUMER_SECRET = data["consumer_secret"]
ACCESS_KEY = data["access_key"]
ACCESS_SECRET = data["access_secret"]

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)

# authorize twitter, initialize tweepy
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

graph = None

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_all_tweets(screen_name):
    # Twitter only allows access to a users most recent 3240 tweets with this method
    print ("getting all tweets from %s into csv file..." % screen_name)

    ensure_dir("csv/")
    ensure_dir("txt/")
    ensure_dir("png/")

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
    # print dir(tweet.entities)
    hashtags_found = 0
    hashtags_file = open("txt/"+screen_name+"_hashtags_only.txt", "w")
    for tweet in alltweets:
        # print " HASHTAGS: "+str(tweet.entities['hashtags'])
        hashtags = tweet.entities['hashtags']
        for hashtag in hashtags:
            print ("   #"+hashtag['text'])
            hashtags_file.write(unidecode(hashtag['text'])+"\n")
            hashtags_found += 1
    hashtags_file.close()
    Global.hashtags_found = hashtags_found


    # write the csv
    with open("csv/"+'%s_tweets.csv' % screen_name, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "created_at", "retweets", "favorites", "text"])
        writer.writerows(outtweets)
    pass


def getSeconds(time_str):
    h, m, s = time_str.split(':')
    return int(h)*3600 + int(m)*60 + int(s)


def analyze_csv(screen_name):
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
        stop_words = {"a":0, "about":0, "above":0, "above":0, "across":0, "after":0,
        "afterwards":0, "again":0, "against":0, "all":0, "almost":0, "alone":0, "along":0,
        "already":0, "also":0, "although":0,"always":0,"am":0,"among":0, "amongst":0, "amoungst":0,
        "amount":0,  "an":0, "and":0,"another":0, "any":0,"anyhow":0,"anyone":0,"anything":0,
        "anyway":0, "anywhere":0, "are":0, "around":0, "as":0,  "at":0, "back":0,"be":0,"became":0,
        "because":0,"become":0,"becomes":0, "becoming":0, "been":0, "before":0, "beforehand":0,
        "behind":0, "being":0, "below":0, "beside":0, "besides":0, "between":0, "beyond":0,"bill":0,
        "both":0, "bottom":0,"but":0, "by":0, "call":0, "can":0, "cannot":0, "cant":0, "co":0, "con":0,
        "could":0, "couldnt":0, "cry":0, "de":0, "describe":0, "detail":0, "do":0, "done":0, "down":0,
        "due":0, "during":0, "each":0, "eg":0, "eight":0, "either":0, "eleven":0,"else":0,
        "elsewhere":0, "empty":0, "enough":0, "etc":0, "even":0, "ever":0, "every":0, "everyone":0,
        "everything":0, "everywhere":0, "except":0, "few":0, "fifteen":0, "fify":0, "fill":0,
        "find":0, "fire":0, "first":0, "five":0, "for":0, "former":0, "formerly":0, "forty":0,
        "found":0, "four":0, "from":0, "front":0, "full":0, "further":0, "get":0, "give":0, "go":0,
        "had":0, "has":0, "hasnt":0, "have":0, "he":0, "hence":0, "her":0, "here":0, "hereafter":0,
        "hereby":0, "herein":0, "hereupon":0, "hers":0, "herself":0, "him":0, "himself":0, "his":0,
        "how":0, "however":0, "hundred":0, "ie":0, "if":0, "in":0, "inc":0, "indeed":0, "interest":0,
        "into":0, "is":0, "it":0, "its":0, "itself":0, "keep":0, "last":0, "latter":0, "latterly":0,
        "least":0, "less":0, "ltd":0, "made":0, "many":0, "may":0, "me":0, "meanwhile":0, "might":0,
        "mill":0, "mine":0, "more":0, "moreover":0, "most":0, "mostly":0, "move":0, "much":0,
        "must":0, "my":0, "myself":0, "name":0, "namely":0, "neither":0, "never":0,
        "nevertheless":0, "next":0, "nine":0, "no":0, "nobody":0, "none":0, "noone":0, "nor":0,
        "not":0, "nothing":0, "now":0, "nowhere":0, "of":0, "off":0, "often":0, "on":0, "once":0,
        "one":0, "only":0, "onto":0, "or":0, "other":0, "others":0, "otherwise":0, "our":0, "ours":0,
        "ourselves":0, "out":0, "over":0, "own":0,"part":0, "per":0, "perhaps":0, "please":0, "put":0,
        "rather":0, "re":0, "same":0, "see":0, "seem":0, "seemed":0, "seeming":0, "seems":0,
        "serious":0, "several":0, "she":0, "should":0, "show":0, "side":0, "since":0, "sincere":0,
        "six":0, "sixty":0, "so":0, "some":0, "somehow":0, "someone":0, "something":0, "sometime":0,
        "sometimes":0, "somewhere":0, "still":0, "such":0, "system":0, "take":0, "ten":0, "than":0,
        "that":0, "the":0, "their":0, "them":0, "themselves":0, "then":0, "thence":0, "there":0,
        "thereafter":0, "thereby":0, "therefore":0, "therein":0, "thereupon":0, "these":0,
        "they":0, "thickv":0, "thin":0, "third":0, "this":0, "those":0, "though":0, "three":0,
        "through":0, "throughout":0, "thru":0, "thus":0, "to":0, "together":0, "too":0, "top":0,
        "toward":0, "towards":0, "twelve":0, "twenty":0, "two":0, "un":0, "under":0, "until":0,
        "up":0, "upon":0, "us":0, "very":0, "via":0, "was":0, "we":0, "well":0, "were":0, "what":0,
        "whatever":0, "when":0, "whence":0, "whenever":0, "where":0, "whereafter":0, "whereas":0,
        "whereby":0, "wherein":0, "whereupon":0, "wherever":0, "whether":0, "which":0, "while":0,
        "whither":0, "who":0, "whoever":0, "whole":0, "whom":0, "whose":0, "why":0, "will":0,
        "with":0, "within":0, "without":0, "would":0, "yet":0, "you":0, "your":0, "yours":0,
        "yourself":0, "yourselves":0, "the":0, "RT":0, "co":0, "CO":0,
        'vuelva':0,'realizar':0,'vimos':0,'semana':0,'pasada':0,'luego':0,'dices':0,'k':0,
        'poner':0,'hablamos':0,'favor':0,'sale':0,'digo':0,'miro':0,'tarde':0,'saludo':0,
        'dejan':0,'dado':0,'quería':0,'necesitaría':0,'decir':0,'día':0,'hacerlo':0,'hace':0,
        'muchas':0,'pedimos':0,'ido':0,'genial':0,'preguntar':0,'quedo':0,'pasa':0,'días':0,
        'tardes':0,'buenas':0,'necesito':0,'buenos':0,'hola':0,'gracias':0,'quieres':0,
        'quiero':0,'de':0,'la':0,'que':0,'el':0,'en':0,'y':0,'a':0,'los':0,'del':0,'se':0,'las':0,'por':0,
        'un':0,'para':0,'con':0,'no':0,'una':0,'su':0,'al':0,'lo':0,'como':0,'más':0,'pero':0,'sus':0,
        'le':0,'ya':0,'o':0,'este':0,'sí':0,'porque':0,'esta':0,'entre':0,'cuando':0,'muy':0,'sin':0,
        'sobre':0,'también':0,'me':0,'hasta':0,'hay':0,'donde':0,'quien':0,'desde':0,'todo':0,
        'nos':0,'durante':0,'todos':0,'uno':0,'les':0,'ni':0,'contra':0,'otros':0,'ese':0,'eso':0,
        'ante':0,'ellos':0,'e':0,'esto':0,'mí':0,'antes':0,'algunos':0,'qué':0,'unos':0,'yo':0,
        'otro':0,'otras':0,'otra':0,'él':0,'tanto':0,'esa':0,'estos':0,'mucho':0,'quienes':0,
        'nada':0,'muchos':0,'cual':0,'poco':0,'ella':0,'estar':0,'estas':0,'algunas':0,'algo':0,
        'nosotros':0,'mi':0,'mis':0,'tú':0,'te':0,'ti':0,'tu':0,'tus':0,'ellas':0,'nosotras':0,
        'vosotros':0,'vosotras':0,'os':0,'mío':0,'mía':0,'míos':0,'mías':0,'tuyo':0,'tuya':0,
        'tuyos':0,'tuyas':0,'suyo':0,'suya':0,'suyos':0,'suyas':0,'nuestro':0,'nuestra':0,
        'nuestros':0,'nuestras':0,'vuestro':0,'vuestra':0,'vuestros':0,'vuestras':0,'esos':0,
        'esas':0,'estoy':0,'estás':0,'está':0,'estamos':0,'estáis':0,'están':0,'esté':0,'estés':0,
        'estemos':0,'estéis':0,'estén':0,'estaré':0,'estarás':0,'estará':0,'estaremos':0,
        'estaréis':0,'estarán':0,'estaría':0,'estarías':0,'estaríamos':0,'estaríais':0,
        'estarían':0,'estaba':0,'estabas':0,'estábamos':0,'estabais':0,'estaban':0,'estuve':0,
        'estuviste':0,'estuvo':0,'estuvimos':0,'estuvisteis':0,'estuvieron':0,'estuviera':0,
        'estuvieras':0,'estuviéramos':0,'estuvierais':0,'estuvieran':0,'estuviese':0,
        'estuvieses':0,'estuviésemos':0,'estuvieseis':0,'estuviesen':0,'estando':0,
        'estado':0,'estada':0,'estados':0,'estadas':0,'estad':0,'he':0,'has':0,'ha':0,'hemos':0,
        'habéis':0,'han':0,'haya':0,'hayas':0,'hayamos':0,'hayáis':0,'hayan':0,'habré':0,
        'habrás':0,'habrá':0,'habremos':0,'habréis':0,'habrán':0,'habría':0,'habrías':0,
        'habríamos':0,'habríais':0,'habrían':0,'había':0,'habías':0,'habíamos':0,'habíais':0,
        'habían':0,'hube':0,'hubiste':0,'hubo':0,'hubimos':0,'hubisteis':0,'hubieron':0,
        'hubiera':0,'hubieras':0,'hubiéramos':0,'hubierais':0,'hubieran':0,'hubiese':0,
        'hubieses':0,'hubiésemos':0,'hubieseis':0,'hubiesen':0,'habiendo':0,'habido':0,
        'habida':0,'habidos':0,'habidas':0,'soy':0,'eres':0,'es':0,'somos':0,'sois':0,'son':0,
        'sea':0,'seas':0,'seamos':0,'seáis':0,'sean':0,'seré':0,'serás':0,'será':0,'seremos':0,
        'seréis':0,'serán':0,'sería':0,'serías':0,'seríamos':0,'seríais':0,'serían':0,'era':0,
        'eras':0,'éramos':0,'erais':0,'eran':0,'fui':0,'fuiste':0,'fue':0,'fuimos':0,'fuisteis':0,
        'fueron':0,'fuera':0,'fueras':0,'fuéramos':0,'fuerais':0,'fueran':0,'fuese':0,
        'fueses':0,'fuésemos':0,'fueseis':0,'fuesen':0,'siendo':0,'sido':0,'tengo':0,'tienes':0,
        'tiene':0,'tenemos':0,'tenéis':0,'tienen':0,'tenga':0,'tengas':0,'tengamos':0,
        'tengáis':0,'tengan':0,'tendré':0,'tendrás':0,'tendrá':0,'tendremos':0,'tendréis':0,
        'tendrán':0,'tendría':0,'tendrías':0,'tendríamos':0,'tendríais':0,'tendrían':0,
        'tenía':0,'tenías':0,'teníamos':0,'teníais':0,'tenían':0,'tuve':0,'tuviste':0,'tuvo':0,
        'tuvimos':0,'tuvisteis':0,'tuvieron':0,'tuviera':0,'tuvieras':0,'tuviéramos':0,
        'tuvierais':0,'tuvieran':0,'tuviese':0,'tuvieses':0,'tuviésemos':0,'tuvieseis':0,
        'tuviesen':0,'teniendo':0,'tenido':0,'tenida':0,'tenidos':0,'tenidas':0,'tened':0,
        'ahí':0,'ajena':0,'ajeno':0,'ajenas':0,'ajenos':0,'algúna':0,'allá':0,'ambos':0,
        'aquello':0,'aquellas':0,'aquellos':0,'así':0,'atrás':0,'aun':0,'aunque':0,'bajo':0,
        'bastante':0,'bien':0,'cabe':0,'cada':0,'casi':0,'cierto':0,'cierta':0,'ciertos':0,
        'ciertas':0,'conmigo':0,'conseguimos':0,'conseguir':0,'consigo':0,'consigue':0,
        'consiguen':0,'consigues':0,'cualquier':0,'cualquiera':0,'cualquieras':0,'cuan':0,
        'cuanto':0,'cuanta':0,'cuantas':0,'cuantos':0,'de':0,'dejar':0,'demás':0,'demasiadas':0,
        'demasiados':0,'dentro':0,'dos':0,'ello':0,'emplean':0,'emplear':0,'empleas':0,
        'encima':0,'entonces':0,'era':0,'eras':0,'eramos':0,'eses':0,'estes':0,'gueno':0,
        'hacer':0,'hacemos':0,'hacia':0,'hago':0,'incluso':0,'intenta':0,'intentas':0,
        'intentamos':0,'intentan':0,'intento':0,'ir':0,'mismo':0,'ningúno':0,'nunca':0,
        'parecer':0,'podemos':0,'podría':0,'podrías':0,'podríais':0,'podríamos':0,'podrían':0,
        'primero':0,'puedes':0,'pueden':0,'pues':0,'querer':0,'quiénes':0,'quienesquiera':0,
        'quienquiera':0,'quizás':0,'sabe':0,'sabes':0,'saben':0,'sabéis':0,'sabemos':0,
        'saber':0,'sino':0,'solo':0,'esta':0,'tampoco':0,'tan':0,'tanta':0,'tantas':0,'tantos':0,
        'tener':0,'tiempo':0,'toda':0,'todas':0,'tomar':0,'trabaja':0,'trabajas':0,'tras':0,
        'último':0,'ultimo':0,'última':0,'ultima':0,'unas':0,'ustedes':0,'variasos':0,
        'verdadera':0,'pocas':0,'pocos':0,'podéis':0,'podemos':0,'poder':0,'podría':0,
        'podrías':0,'podríais':0,'podríamos':0,'podrían':0,'primero':0,'puede':0,'puedo':0,
        'pueda':0,'pues':0,'querer':0,'quiénes':0,'quienesquiera':0,'quienquiera':0,
        'quizás':0,'mas':0,'sabe':0,'sabes':0,'saben':0,'sabéis':0,'sabemos':0,'saber':0,
        'según':0,'ser':0,'si':0,'siempre':0,'sino':0,'so':0,'solamente':0,'solo':0,'sólo':0,'sr':0,
        'sra':0,'sres':0,'sta':0,'tal':0,'tales':0,'tampoco':0,'tan':0,'tanta':0,'tantas':0,
        'tantos':0,'tener':0,'tiempo':0,'toda':0,'den':0,'queria':0,'todas':0,'tomar':0,
        'trabaja':0,'trabajo':0,'trabajáis':0,'trabajamos':0,'trabajan':0,'trabajar':0,
        'trabajas':0,'tras':0,'último':0,'ultimo':0,'unas':0,'usa':0,'usas':0,'usáis':0,
        'usamos':0,'usan':0,'usar':0,'uso':0,'usted':0,'ustedes':0,'va':0,'van':0,'vais':0,
        'valor':0,'vamos':0,'varias':0,'varias':0,'varios':0,'vaya':0,'verdadera':0,'voy':0,
        'vez':0,'más':0,'ok':0}
        for row in readCSV:
            rows += 1
            date = row[1]
            retweets = row[2]
            favorites = row[3]
            tweetText = row[4]
            if(tweetText != "text"):
                for word in tweetText.split(" "):
                    if("#" not in word and "@" not in word and "co" not in word and "http" not in word and word not in stop_words):
                        tweets_file.write(word+" ")
                tweets_file.write("\n\n")
                if(rows < 7):
                    Global.five_latest_tweets[rows-2] = tweetText
                    Global.five_latest_dates[rows-2] = str(date).split(' ')[0]
                    Global.five_latest_retweets[rows-2] = retweets
                    Global.five_latest_likes[rows-2] = favorites
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
        generate_word_cloud(screen_name, "tweets")
        if(Global.hashtags_found > 0):
            generate_word_cloud(screen_name, "hashtags")
        numTweets = rows - 1
        if(numTweets >= 1):
            readCSV = csv.reader(open("csv/"+screen_name+'_tweets.csv'), delimiter=',')
            row_1 = next(itertools.islice(readCSV, numTweets, numTweets+1))
            print(" 1st tweet: %s" % row_1[4])
            first_tweet_date = datetime.datetime.strptime(row_1[1], "%Y-%m-%d %H:%M:%S")
            Global.first_tweet_month = first_tweet_date.month
            Global.first_tweet_year = first_tweet_date.year
            account_created_date = datetime.datetime.strptime(Global.created_at, "%Y-%m-%d %H:%M:%S")
            date_delta = first_tweet_date - account_created_date
            print("1st tweet date: %s" % first_tweet_date)
            print("account created date: %s" % account_created_date)
            print("time taken to make 1st tweet: %s DAYS %s SECONDS" % (str(date_delta.days), str(date_delta.seconds)))
            if(date_delta.days > 364):  # more than a year
                Global.time_taken_1st_tweet = "{0:.1f} YEARS".format(date_delta.days/365.00)
            elif(date_delta.days > 30):  # mora than a month
                Global.time_taken_1st_tweet = "{0:.1f} MONTHS".format(date_delta.days/30.00)
            elif(date_delta.days > 0):  # more than a day
                Global.time_taken_1st_tweet = "%d DAYS" % date_delta.days
            elif(date_delta.seconds > 3599):  # more than an hour
                Global.time_taken_1st_tweet = "{0:.1f} HOURS".format(date_delta.seconds/3600)
            elif(date_delta.seconds > 59):  # more than a minute
                Global.time_taken_1st_tweet = "{0:.1f} MINUTES".format(date_delta.seconds/60)
            else:  # more than a second
                Global.time_taken_1st_tweet = "%d SECONDS" % date_delta.seconds
        if(numTweets >= 100):
            readCSV = csv.reader(open("csv/"+screen_name+'_tweets.csv'), delimiter=',')
            row_100 = next(itertools.islice(readCSV, numTweets-100, numTweets-99))
            print(" 100th tweet: %s" % row_100[4])
            tweet_100_date = datetime.datetime.strptime(row_100[1], "%Y-%m-%d %H:%M:%S")
            Global.cien_tweet_month = tweet_100_date.month
            Global.cien_tweet_year = tweet_100_date.year
            date_delta = tweet_100_date - first_tweet_date
            print("100th tweet date: %s" % tweet_100_date)
            print("1st tweet date date: %s" % first_tweet_date)
            print("from then, time taken to make 100 tweets: %s DAYS %s SECONDS" % (str(date_delta.days), str(date_delta.seconds)))
            if(date_delta.days > 364):
                Global.time_taken_100_tweets = "{0:.1f} YEARS".format(date_delta.days/365.00)
            elif(date_delta.days > 30):
                Global.time_taken_100_tweets = "{0:.1f} MONTHS".format(date_delta.days/30.00)
            elif(date_delta.days > 0):  # more than a day
                Global.time_taken_100_tweets = "%d DAYS" % date_delta.days
            elif(date_delta.seconds > 3599):  # more than an hour
                Global.time_taken_100_tweets = "{0:.1f} HOURS".format(date_delta.seconds/3600)
            elif(date_delta.seconds > 59):  # more than a minute
                Global.time_taken_100_tweets = "{0:.1f} MINUTES".format(date_delta.seconds/60)
            else:  # more than a second
                Global.time_taken_100_tweets = "%d SECONDS" % date_delta.seconds
        averageSeconds = totalTime/numTweets  # don't count the first line
        average24HrFormat = str(datetime.timedelta(seconds=averageSeconds))
        averageRetweets = totalRetweets/(numTweets)  # don't count the first line
        averageFavorites = totalFavorites/(numTweets)  # don't count the first line
        Global.tweets = str(numTweets)
        Global.average_tweet_time = average24HrFormat
        Global.average_tweet_retweets = str(averageRetweets)
        Global.average_tweet_favorites = str(averageFavorites)
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
            print ("Rate limit reached!")
            break


def get_user_info(screen_name):
    # get user's info
    user = api.get_user(screen_name)
    screen_name = user.screen_name
    description = emoji_pattern.sub(r'', user.description)  # no emoji
    followers = user.followers_count
    following = user.friends_count
    profile_image_url = user.profile_image_url.replace("normal", "200x200")
    location = user.location
    verified = user.verified
    created_at = user.created_at

    # app = App.get_running_app()
    Global.image_url = profile_image_url
    Global.screen_name = screen_name
    if(description != ""):
        Global.description = unidecode(description)  # no accents
    if(location != ""):
        Global.location = unidecode(location)
    Global.verified = str(verified)
    Global.created_at = str(created_at)
    Global.created_at_month = created_at.month
    Global.created_at_year = created_at.year
    Global.followers = str(followers)
    Global.following = str(following)

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

    tx = graph.cypher.begin()
    tx.append("OPTIONAL MATCH(n) WHERE n.name={target} RETURN CASE n WHEN null THEN 0 ELSE 1 END as result", target=screen_name)
    target_exists = tx.commit()[0][0][0]
    tx = graph.cypher.begin()
    if(target_exists != 1):
        tx.append("CREATE (target:Origin:User {name:{target}}) RETURN target", target=screen_name)
        target = tx.commit()[0].one
    else:
        tx.append("MATCH(target) WHERE target.name={target} RETURN target", target=screen_name)
        target = tx.commit()[0].one
    fishy_followers = 0
    for follower in handle_limit(tweepy.Cursor(api.followers, screen_name=screen_name, count=MAX_RETRIEVE_FOLLOWERS).items()):
        num_follower += 1
        if(num_follower > MAX_RETRIEVE_FOLLOWERS):
            break
        print ("followed by: #%d %s" % (num_follower, follower.screen_name))
        print ("  tweets: %d" % follower.statuses_count)
        print ("  followers: %d" % follower.followers_count)
        print ("  following: %d" % follower.friends_count)
        print ("  location: %s" % follower.location)
        if(follower.statuses_count == 0 and follower.followers_count < 10):
            print ("  FISHY follower...")
            fishy_followers += 1
        tx = graph.cypher.begin()
        tx.append("OPTIONAL MATCH(n) WHERE n.name={origin} RETURN CASE n WHEN null THEN 0 ELSE 1 END as result", origin=follower.screen_name)
        origin_exists = tx.commit()[0][0][0]
        tx = graph.cypher.begin()

        tx = graph.cypher.begin()
        tx.append("OPTIONAL MATCH(origin {name:{origin}}) -[rel:FOLLOWS]->(target {name:{target}}) RETURN CASE rel WHEN null THEN 0 ELSE 1 END as result", origin=follower.screen_name, target=screen_name)
        relationship_exists = tx.commit()[0][0][0]
        tx = graph.cypher.begin()

        if(origin_exists != 1):
            # print "   node doesnt exist yet"
            tx.append("CREATE (origin:User {name:{origin}}) RETURN origin", origin=follower.screen_name)
            tx.commit()
            tx = graph.cypher.begin()
        if(relationship_exists != 1):
            # print "   relationship doesnt exist yet"
            tx.append("MATCH(origin) where origin.name={origin} RETURN origin", origin=follower.screen_name)
            origin = tx.commit()[0].one
            follows_relationship = Path(origin, "FOLLOWS", target)
            graph.create(follows_relationship)
        if api.show_friendship(source_screen_name=screen_name, target_screen_name=follower.screen_name)[0].following:  # user follows back this follower
            # print "%s follows %s back!" % (screen_name, follower.screen_name)
            followback_total += 1
    # print("total follows back: %d     followers: %d     num_follower: %d" % (followback_total, followers, num_follower))
    Global.followback_total = followback_total
    Global.fishy_followers = fishy_followers
    if followers == MAX_RETRIEVE_FOLLOWERS or followers < MAX_RETRIEVE_FOLLOWERS:
        followback_percentage = (followback_total*100)/followers
        Global.followback_percentage = "from all of %s's %d followers, %d have been followed back, %d%% of them" % (screen_name, followers, followback_total, followback_percentage)
        print("from all of %s's %d followers, %d have been followed back, %d%% of them" % (screen_name, followers, followback_total, followback_percentage))
    else:  # only the newest followers will were examined, to avoid reaching the API's rate limit
        followback_percentage = (followback_total*100)/MAX_RETRIEVE_FOLLOWERS
        Global.followback_percentage = "from %s's newest %d followers, %d have been followed back, %d%% of them" % (screen_name, MAX_RETRIEVE_FOLLOWERS, followback_total, followback_percentage)
        print("from %s's newest %d followers, %d have been followed back, %d%% of them" % (screen_name, MAX_RETRIEVE_FOLLOWERS, followback_total, followback_percentage))
    return user.screen_name


def generate_word_cloud(screen_name, type):
    d = os.path.dirname(__file__)

    # Read the whole text.
    tweetsText = open(os.path.join(d, "txt/"+screen_name+"_"+type+"_only.txt")).read()

    wordcloud = WordCloud(max_font_size=40, collocations=False).generate(tweetsText)
    figure = plt.figure(dpi=300)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    # plt.show()
    figure.savefig("png/"+screen_name+"_"+type+"_word_cloud.png", bbox_inches='tight', transparent=True, pad_inches=0, dpi=300)
    if(type == "tweets"):
        Global.wordcloud_tweets_image = "png/"+screen_name+"_tweets_word_cloud.png"
    else:
        Global.wordcloud_hashtags_image = "png/"+screen_name+"_hashtags_word_cloud.png"

def neo4j_follows(screen_name):
    print("analyzing follows of %s..." % screen_name)

    tx = graph.cypher.begin()
    tx.append("OPTIONAL MATCH(n) WHERE n.name={origin} RETURN CASE n WHEN null THEN 0 ELSE 1 END as result", origin=screen_name)
    origin_exists = tx.commit()[0][0][0]
    tx = graph.cypher.begin()
    if(origin_exists != 1):
        tx.append("CREATE (origin:Origin:User {name:{origin}}) RETURN origin", origin=screen_name)
        origin = tx.commit()[0].one
    else:
        tx.append("MATCH(origin) WHERE origin.name={origin} SET origin:Origin:User RETURN origin", origin=screen_name)
        origin = tx.commit()[0].one
    tx = graph.cypher.begin()

    screen_names = []
    MAX_RETRIEVE_FOLLOWING = 100
    following_found = 0
    for following in tweepy.Cursor(api.friends, screen_name=screen_name, count=100).items():
        following_found += 1
        # print "  following #" + str(following_found) + ": " + following.screen_name
        if(following_found >= MAX_RETRIEVE_FOLLOWING):
            break
        screen_names.append(following.screen_name)
    # print "SCREEN NAMES: "
    for follow_screen_name in screen_names:
        # print " "+follow_screen_name

        tx = graph.cypher.begin()
        tx.append("OPTIONAL MATCH(n) WHERE n.name={target} RETURN CASE n WHEN null THEN 0 ELSE 1 END as result", target=follow_screen_name)
        target_exists = tx.commit()[0][0][0]
        tx = graph.cypher.begin()

        tx = graph.cypher.begin()
        tx.append("OPTIONAL MATCH(origin {name:{origin}}) -[rel:FOLLOWS]->(target {name:{target}}) RETURN CASE rel WHEN null THEN 0 ELSE 1 END as result", origin=screen_name, target=follow_screen_name)
        relationship_exists = tx.commit()[0][0][0]
        tx = graph.cypher.begin()

        if(target_exists != 1):
            # print "   node doesnt exist yet"
            tx.append("CREATE (target:User {name:{target}}) RETURN target", target=follow_screen_name)
            tx.commit()
            tx = graph.cypher.begin()
        if(relationship_exists != 1):
            # print "   relationship doesnt exist yet"
            tx.append("MATCH(target) where target.name={target} RETURN target", target=follow_screen_name)
            target = tx.commit()[0].one
            follows_relationship = Path(origin, "FOLLOWS", target)
            graph.create(follows_relationship)


if __name__ == '__main__':
    # pass in the username of the account you want to analyze and the password for your neo4j database
    screen_name = sys.argv[1]
    psswrd = sys.argv[2]
    authenticate("localhost:7474", "neo4j", psswrd)
    graph = Graph("http://localhost:7474/db/data/")
    screen_name = get_user_info(screen_name)
    get_all_tweets(screen_name)
    analyze_csv(screen_name)
    neo4j_follows(screen_name)
    Twitter_AnalysisApp().run()
