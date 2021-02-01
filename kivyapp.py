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
import client
from kivy.clock import Clock
import sys

kivy.require("2.0.0")

class ConnectPage(GridLayout):
    # runs on initialization
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if os.path.isfile("prev_details.txt"):
            with open("prev_details.txt", "r") as f:
                d = f.read().split(",")
                prev_ip = d[0]
                prev_port = d[1]
                prev_username = d[2]
        else:
            prev_ip = ""
            prev_port = ""
            prev_username = ""

        self.cols = 2
        self.add_widget(Label(text='IP:'))
        self.ip = TextInput(text=prev_ip,multiline=False)
        self.add_widget(self.ip)

        self.add_widget(Label(text='Port:'))
        self.port = TextInput(text=prev_port, multiline=False)
        self.add_widget(self.port)

        self.add_widget(Label(text='Username:'))
        self.username = TextInput(text=prev_username, multiline=False)
        self.add_widget(self.username)

        # Setting up button
        self.join = Button(text="Join")
        self.join.bind(on_press=self.join_button)
        self.add_widget(Label())
        self.add_widget(self.join)

    def join_button(self, instance):
        ip = self.ip.text
        port = self.port.text
        username = self.username.text

        with open("prev_details.txt", "w") as f:
            f.write(f"{ip},{port},{username}")
        # print(f"Joining {ip}:{port} as {username}")

        info = f"Joining {ip}:{port} as {username}"
        chat_app.info_page.update_info(info)
        chat_app.screen_manager.current = 'Info'
        Clock.schedule_once(self.connect, 1)


    def connect(self, _):
        IP = self.ip.text
        PORT = int(self.port.text)
        username = self.username.text

        if not client.connect(IP, PORT, username, show_err):
            return

        chat_app.create_chat_page()
        chat_app.screen_manager.current = "Chat"    

class ScrollableView(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = GridLayout(cols=1, size_hint_y=None)
        self.add_widget(self.layout)

        # Widget for chat history and scroll to widget
        self.chat_history = Label(size_hint_y=None, markup=True)
        self.scroll_to_point = Label

        self.add_widget(self.chat_history)
        self.add_widget(self.scroll_to_point)

    # Called externally
    def update_chat_history(self, message):
        self.chat_history += '\n' + message

        # Add padding
        self.layout.height = self.chat_history.texture_size[1] +15            
        self.chat_history.height = self.chat_history.texture_size[1]
        self.chat_history.text_size = (self.chat_history.width * 0.98, None)

        # Scroo to piont required because their is no inbuilt function for this
        self.scroll_to(self.scroll_to_point)

class ChatPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 1
        self.rows = 2

        # take 90% of height
        self.history = Label(height = Window.size[1]*0.9, size_hint_y=None)
        self.add_widget(self.history)

        self.message = TextInput(width = Window.size[0]*0.8, size_hint_x=None, multiline=False)
        self.send = Button(text="Send")
        self.send.bind(on_press= self.send_message)

        # Inserting two columns under one row
        bottom_line = GridLayout(cols=2)
        bottom_line.add_widget(self.message)
        bottom_line.add_widget(self.send)
        self.add_widget(bottom_line)

        self.bind(size=self.adjust_fields)

        Window.bind(on_key_down=self.on_key_down)

        # We also want to focus on our text input field
        Clock.schedule_once(self.focus_text_input, 1)
        client.start_listening(self.incoming_message, show_err)
    
    def adjust_fields(self, *_):
        if Window.size[1] * 0.1 < 50:
            new_height = Window.size[1] - 50
        else:
            new_height = Window.size[1] * 0.9
        self.history.height = new_height

        if Window.size[0] * 0.2 < 160:
            new_width = Window.size[0] - 160
        else:
            new_width = Window.size[0] * 0.8
        self.new_message.width = new_width

        # Update chat history layout
        #self.history.update_chat_history_layout()
        Clock.schedule_once(self.history.update_chat_history_layout, 0.01)

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):

        # But we want to take an action only when Enter key is being pressed, and send a message
        if keycode == 40:
            self.send_message(None)

    # Gets called when either Send button or Enter key is being pressed
    def send_message(self, _):
        #Clear input field
        message = self.new_message.text
        self.new_message.text = ''

        # If there is any message - add it to chat history and send to the server
        if message:
            # Our messages - use red color for the name
            self.history.update_chat_history(f'[color=dd2020]{chat_app.connect_page.username.text}[/color] > {message}')
            client.send(message)

        Clock.schedule_once(self.focus_text_input, 0.1)


    # Sets focus to text input field
    def focus_text_input(self, _):
        self.new_message.focus = True

    def incoming_message(self, username, message):
        # Update chat history with username and message, green color for username
        self.history.update_chat_history(f'[color=20dd20]{username}[/color] > {message}')

class InfoPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 1
        self.message = Label(halign="center", valign="middle", font_size=30)

        # By default every widget returns it's side as [100, 100], it gets finally resized,
        # but we have to listen for size change to get a new one
        self.message.bind(width=self.update_text_width)
        self.add_widget(self.message)

    def update_info(self, message):
        self.message.text = message

    def update_text_width(self, *_):
        self.message.text_size = (self.message.width * 0.9, None)

class EpicApp(App):
    def build(self):
        # Creating a page and screen then adding page to screen
        self.screen_manager = ScreenManager()
        self.connect_page = ConnectPage()
        screen = Screen(name='Connect')
        screen.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen)

        #Info page
        self.info_page = InfoPage()
        screen = Screen(name='Info')
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)
        return self.screen_manager

    def create_chat_page(self):
        self.chat_page = ChatPage()
        screen = Screen(name="Chat")
        screen.add_widget(self.chat_page)
        self.screen_manager.add_widget(screen)

def show_err(msg):
    chat_app.info_page.update_info(msg)
    chat_app.screen_manager.current = "Info"
    Clock.schedule_once(sys.exit, 10)

if __name__ == '__main__':
    chat_app = EpicApp()
    chat_app.run()