#!/usr/bin/env python3

from kivy.app import App
from kivy.uix.pagelayout import PageLayout
from kivy.properties import StringProperty

# Import terawatt model
from model import *

class Controller(PageLayout):

    label_photovoltaic = StringProperty("0")

    def __init__(self):
        # Call init of parent class
        super(PageLayout, self).__init__()
        self.model = Model()

        self.label_photovoltaic = str(self.model.photovoltaic.energy_now.electrical)

    def callback_weather(self, *args):
        print("Show the weather forecast")

    def callback_photovoltaic(self, *args):
        print("Access the photovoltaic")
        # FIXME: Just for test
        self.model.increment()
        print(self.model.photovoltaic.energy_now.electrical)
        self.label_photovoltaic = str(self.model.photovoltaic.energy_now.electrical)

    def callback_battery(self, *args):
        print("Access the battery")
        print(self.model.battery.energy_now.electrical)

    def callback_car1(self, *args):
        print("Access the car 1")
        print(self.model.car1.energy_now.electrical)

    def callback_car2(self, *args):
        print("Access the car 2")
        print(self.model.car2.energy_now.electrical)

class TerawattApp(App):

    def build(self):
        return Controller()


if __name__ == '__main__':
    TerawattApp().run()
