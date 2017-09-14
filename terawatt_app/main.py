#!/usr/bin/env python

from kivy.app import App
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.pagelayout import PageLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.properties import NumericProperty

from plyer import notification
from plyer.utils import platform
from plyer.compat import PY2

# Import terawatt model
from model import *


__version__ = "0.2"


class Notification(BoxLayout):

    def do_notify(self, mode='normal'):
        title = self.ids.notification_title.text
        message = self.ids.notification_text.text
        ticker = self.ids.ticker_text.text
        if PY2:
            title = title.decode('utf8')
            message = message.decode('utf8')
        kwargs = {'title': title, 'message': message, 'ticker': ticker}

        notification.notify(**kwargs)


class ImageButton(ButtonBehavior, Image):
    pass


class Controller(PageLayout):

    label_photovoltaic = StringProperty("0")
    label_battery = StringProperty("0")
    label_car1 = StringProperty("0")
    label_car2 = StringProperty("0")
    label_increment = StringProperty("0")
    label_time = StringProperty("0")
    number_increment = NumericProperty(120)

    def __init__(self, **kwargs):
        # Call init of parent class
        super(PageLayout, self).__init__(**kwargs)
        self.model = Model()
        self._update_labels()
        self.notification = Notification()

    def _update_labels(self):
        """
        Update the labels
        """
        txt = round(self.model.photovoltaic.power.electrical,1)
        self.label_photovoltaic = str(txt) + 'W'
        txt = round(self.model.battery.energy_now.electrical,1)
        self.label_battery = str(txt) + 'Wh'
        txt = round(self.model.car1.energy_now.electrical,1)
        self.label_car1 = str(txt) + 'Wh'
        txt = round(self.model.car2.energy_now.electrical,1)
        self.label_car2 = str(txt) + 'Wh'
        txt = round(self.model.car2.energy_now.electrical,1)
        self.label_time = str(self.model.time_current)
        txt = self.number_increment
        self.label_increment = str(txt)

    def callback_weather(self, *args):
        print("Show the weather forecast")

    def callback_photovoltaic(self, *args):
        print("Access the photovoltaic")
        print(self.model.photovoltaic.energy_now.electrical)

    def callback_battery(self, *args):
        print("Access the battery")
        print(self.model.battery.energy_now.electrical)

    def callback_car1(self, *args):
        print("Access the car")
        print(self.model.car1.energy_now.electrical)

    def callback_car2(self, *args):
        print("Access the e-bicycle")
        print(self.model.car2.energy_now.electrical)

    def callback_increment_do(self, *args):
        for i in range(self.number_increment):
            self.model.increment()
        self._update_labels()
        print(self.model.photovoltaic.energy_now.electrical)
        print(self.model.battery.energy_now.electrical)

    def callback_increment_slider(self, instance, value):
        self.number_increment = value
        print(self.number_increment)

    def callback_increment_reset(self, *args):
        self.model = Model()
        self._update_labels()


class TerawattApp(App):

    def build(self):
        return Controller()


if __name__ == '__main__':
    TerawattApp().run()
