import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import os
import twitter_api
from kivy.clock import Clock
import sys

kivy.require("2.0.0")

class HomePage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 1
        self.rows = 2

        # take 90% of height
        self.info = Label(height = Window.size[1]*0.9, size_hint_y=None)
        info = twitter_api.get_user("_10bih")
        self.info += "id: " + str(info.id) + "\n" + "Name: " + info.name + "\n" + "Screen_name: " + info.screen_name + "\n" + "Description : " + info.description
        self.add_widget(self.info)

        self.followers = Button(text="Followers")
        self.friends = Button(text="Friends")

        # Function is yet to be assigned 
        bottom = GridLayout(cols=2)
        bottom.add_widget(self.friends)
        bottom.add_widget(self.followers)
        self.add_widget(bottom)

class QueryPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 1
        self.rows = 2

        # take 90% of height
        self.info = Label(height = Window.size[1]*0.9, size_hint_y=None)
        self.add_widget(self.info)

        self.home = Button(text="Home")

class MainApp(App):
    def build(self):
        # Creating a page and screen then adding page to screen
        self.screen_manager = ScreenManager()
        self.connect_page = HomePage()
        screen = Screen(name='Home')
        screen.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen)

        #Query Page
        self.info_page = QueryPage()
        screen = Screen(name='Query')
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

if __name__ == '__main__':
    MainApp().run()