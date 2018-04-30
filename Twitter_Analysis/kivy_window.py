from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.config import Config
from kivy.uix.carousel import Carousel
import threading
import Global
import timeline


class Widgets(FloatLayout):
    run_carousel = True

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(Widgets, self).__init__(**kwargs)
        Config.set('graphics', 'width', '1800')
        Config.set('graphics', 'height', '900')
        Config.write()

        root = Widget()
        print "root.width: %f" % root.width
        print "root.height: %f" % root.height
        self.add_widget(
            AsyncImage(
                source=str(Global.image_url),
                pos=(-root.width*6, root.height*3.25)
            )
        )
        self.add_widget(
            Label(
                text='@'+str(Global.screen_name),
                pos=(-root.width*6, root.height*2)
            )
        )
        self.add_widget(
            Label(
                text="location: "+str(Global.location),
                pos=(-root.width*6, root.height*1.3)
            )
        )
        self.add_widget(
            Label(
                text="verified: "+str(Global.verified),
                pos=(-root.width*6, root.height*0.9)
            )
        )
        self.add_widget(
            Label(
                text="description:\n"+str(Global.description),
                pos=(-root.width*6, root.height*0.4)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.tweets)+"\ntweets",
                pos=(-root.width*3, root.height*3.5)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.followers)+"\nfollowers",
                pos=(-root.width, root.height*3.5)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.following)+"\nfollowing",
                pos=(root.width, root.height*3.5)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.average_tweet_time)+"\naverage tweet time",
                pos=(root.width*5, root.height*4)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.average_tweet_retweets)+"\naverage retweets in tweets",
                pos=(root.width*5, root.height*3)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.average_tweet_favorites)+"\naverage favorites in tweets",
                pos=(root.width*5, root.height*2)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.followback_percentage),
                pos=(-root.width*.4, root.height*1.5)
            )
        )
        self.add_widget(
            Image(
                source=str(Global.wordcloud_image),
                pos=(-root.width*2, root.height),
                size_hint_y=None,
                height=350
            )
        )
        self.add_widget(
            Label(
                text="on Twitter since: "+str(Global.created_at),
                pos=(-root.width*.6, root.height*1.2)
            )
        )
        self.add_widget(
            Label(
                text="after that, time taken to make 1st tweet: "+str(Global.time_taken_1st_tweet), # TODO: change messages according to the amount of tweets.
                                                                                                    # If account has more than 3240 tweets, we're not really looking
                                                                                                    # at the first tweet, only at the earliest one the Twitter API allows
                pos=(-root.width*.6, root.height)
            )
        )
        self.add_widget(
            Label(
                text="after that, time taken for first 100 tweets: "+str(Global.time_taken_100_tweets), # TODO: change messages according to the amount of tweets.
                                                                                                        # If account has more than 3240 tweets, we're not really looking
                                                                                                        # at the first 100 tweets, only at the earliest one the Twitter API allows
                pos=(-root.width*.6, root.height*.8)
            )
        )
        self.add_widget(
            Label(
                text="most tweets per day: "+str(Global.most_tweets_per_day)+" on "+str(Global.most_tweets_day),
                pos=(-root.width*.6, root.height*0.6)
            )
        )
        self.add_widget(
            Label(
                text="5 most recent tweets: ",
                pos=(-root.width*.6, -root.height*3.5)
            )
        )
        carousel = Carousel(direction='right')
        for i in range(5):
            tweet_layout = FloatLayout()
            tweet_layout.add_widget(
                Label(
                    text="#"+str(i+1)+":\n"+Global.five_latest_tweets[i],
                    pos=(-root.width*.6, -root.height*3.8)
                )
            )
            tweet_layout.add_widget(
                Image(
                source=str('img/date.png'),
                pos=(-root.width*1.8, 0),
                size_hint_y=None,
                height=35
                )
            )
            tweet_layout.add_widget(
                Image(
                    source=str('img/retweets.png'),
                    pos=(-root.width*0.5, 0),
                    size_hint_y=None,
                    height=35
                )
            )
            tweet_layout.add_widget(
                Image(
                    source=str('img/likes.png'),
                    pos=(root.width*0.2, 0),
                    size_hint_y=None,
                    height=35
                )
            )
            tweet_layout.add_widget(
                Label(
                    text=Global.five_latest_dates[i],
                    pos=(-root.width*1.2, -root.height*4.32)
                )
            )
            tweet_layout.add_widget(
                Label(
                    text=Global.five_latest_retweets[i],
                    pos=(-root.width*0.2, -root.height*4.32)
                )
            )
            tweet_layout.add_widget(
                Label(
                    text=Global.five_latest_likes[i],
                    pos=(root.width*0.5, -root.height*4.32)
                )
            )
            carousel.add_widget(tweet_layout)
        carousel.disabled = True
        carousel.opacity = 6
        carousel.loop = True
        self.add_widget(carousel)

        timeline.create()
        self.add_widget(
            Image(
                source='png/'+str(Global.screen_name)+'_gantt.png',
                pos=(root.width*5, root.height*1.5),
                size_hint_y=None,
                height=400
            )
        )

        def printit():
            if(self.run_carousel):
                threading.Timer(5.0, printit).start()
                # print "RUNNING THREAD!"
                carousel.load_next(mode='next')
        printit()


class Twitter_AnalysisApp(App):

    def build(self):
        self.root = root = Widgets()
        root.bind(size=self._update_rect, pos=self._update_rect)

        with root.canvas.before:
            Color(0, .56, .92, .8)  # blue; colors range from 0-1 not 0-255
            self.rect = Rectangle(size=root.size, pos=root.pos)
        return root

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_stop(self):
        Widgets.run_carousel = False
        # print "NOW STOPPING....."
        pass


if __name__ == '__main__':
    Twitter_AnalysisApp().run()
