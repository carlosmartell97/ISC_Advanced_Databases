from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.config import Config


class Widgets(FloatLayout):

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(Widgets, self).__init__(**kwargs)
        Config.set('graphics', 'width', '1500')
        Config.set('graphics', 'height', '800')
        Config.write()

        root = Widget()
        print "root.width: %f" % root.width
        print "root.height: %f" % root.height
        self.add_widget(
            AsyncImage(
                source=kwargs['image_url'],
                pos=(-root.width*6, root.height*2.5)
            )
        )
        self.add_widget(
            Label(
                text=kwargs['screen_name'],
                pos=(-root.width*6, root.height*1.1)
            )
        )
        self.add_widget(
            Label(
                text=kwargs['location'],
                pos=(-root.width*6, root.height*0.2)
            )
        )
        self.add_widget(
            Label(
                text=kwargs['verified'],
                pos=(-root.width*6, -root.height*0.2)
            )
        )
        self.add_widget(
            Label(
                text=kwargs['created_at'],
                pos=(-root.width*6, -root.height*0.6)
            )
        )
        self.add_widget(
            Label(
                text=kwargs['tweets'],
                pos=(-root.width*3, root.height*3)
            )
        )
        self.add_widget(
            Label(
                text=kwargs['followers'],
                pos=(-root.width, root.height*3)
            )
        )
        self.add_widget(
            Label(
                text=kwargs['following'],
                pos=(root.width, root.height*3)
            )
        )
        self.add_widget(
            Label(
                text=kwargs['average_tweet_time'],
                pos=(root.width*5, root.height*3)
            )
        )
        self.add_widget(
            Label(
                text=kwargs['average_tweet_retweets'],
                pos=(root.width*5, root.height*2)
            )
        )
        self.add_widget(
            Label(
                text=kwargs['average_tweet_favorites'],
                pos=(root.width*5, root.height)
            )
        )
        self.add_widget(
            Label(
                text=kwargs['followback_percentage'],
                pos=(-root.width*.4, -root.height)
            )
        )


class Twitter_AnalysisApp(App):

    def build(self):
        self.root = root = Widgets(
            image_url="http://pbs.twimg.com/profile_images/763456040092389376/2VFO3HfR_400x400.jpg",
            screen_name="carlosmartell97",
            location="location: Mexico",
            verified="verified: False",
            created_at="created at: 2012-01-18 04:53:27",
            tweets="717\ntweets",
            followers="66\nfollowers",
            following="80\nfollowing",
            average_tweet_time="11:22:33\naverage tweet time",
            average_tweet_retweets="256\naverage retweets\nin tweets",
            average_tweet_favorites="0\naverage favorites\nin tweets",
            followback_percentage="from carlosmartell97's newest 50 followers, 27 have been followed back, 54% of them"
        )
        root.bind(size=self._update_rect, pos=self._update_rect)

        with root.canvas.before:
            Color(0, .56, .92, .8)  # blue; colors range from 0-1 not 0-255
            self.rect = Rectangle(size=root.size, pos=root.pos)
        return root

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


if __name__ == '__main__':
    Twitter_AnalysisApp().run()
