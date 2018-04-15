from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.config import Config
import Global


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
                source=str(Global.image_url),
                pos=(-root.width*6, root.height*2.5)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.screen_name),
                pos=(-root.width*6, root.height*1.1)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.location),
                pos=(-root.width*6, root.height*0.2)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.verified),
                pos=(-root.width*6, -root.height*0.2)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.created_at),
                pos=(-root.width*6, -root.height*0.6)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.tweets),
                pos=(-root.width*3, root.height*3)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.followers),
                pos=(-root.width, root.height*3)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.following),
                pos=(root.width, root.height*3)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.average_tweet_time),
                pos=(root.width*5, root.height*3)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.average_tweet_retweets),
                pos=(root.width*5, root.height*2)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.average_tweet_favorites),
                pos=(root.width*5, root.height)
            )
        )
        self.add_widget(
            Label(
                text=str(Global.followback_percentage),
                pos=(-root.width*.4, root.height)
            )
        )
        self.add_widget(
            Image(
                source=str(Global.wordcloud_image),
                pos=(root.width*2, root.height*.2),
                size_hint_y=None,
                height=350
            )
        )


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


if __name__ == '__main__':
    Twitter_AnalysisApp().run()
