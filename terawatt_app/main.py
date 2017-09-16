#!/usr/bin/env python

from kivy.app import App
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.pagelayout import PageLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivy.properties import NumericProperty
from kivy.clock import Clock

from plyer import notification
from plyer.utils import platform
from plyer.compat import PY2

# Import terawatt model
from modelElectrical import *
from modelThermal import *


__version__ = "0.3"


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

class NotificationRadiator(BoxLayout):

    def do_notify(self, heizung):
        title = self.ids.notification_title.text
        message = self.ids.notification_text.text
        ticker = self.ids.ticker_text.text
        if PY2:
            title = title.decode('utf8')
            message = message.decode('utf8')
        message = message + heizung
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
    number_increment = NumericProperty(15)

    label_radiator1_power = StringProperty("0")
    label_radiator2_power = StringProperty("0")
    label_radiator3_power = StringProperty("0")

    def __init__(self, **kwargs):
        # Call init of parent class
        super(Controller, self).__init__(**kwargs)
        self.modelElectrical = ModelElectrical()
        self.modelThermal1 = ModelThermal(room_power_out=10)
        self.modelThermal2 = ModelThermal(room_power_out=20)
        self.modelThermal3 = ModelThermal(room_power_out=100)
        self._update_labels_electrical()
        self.notification = Notification()
        self.notificationRadiator = NotificationRadiator()
        self.radiator_monitoring_running = False

    def _update_labels_electrical(self):
        """
        Update the labels
        """
        txt = round(self.modelElectrical.photovoltaic.power.electrical,1)
        self.label_photovoltaic = str(txt) + 'W'
        txt = round(self.modelElectrical.battery.energy_now.electrical,1)
        self.label_battery = str(txt) + 'Wh'
        txt = round(self.modelElectrical.car1.energy_now.electrical,1)
        self.label_car1 = str(txt) + 'Wh'
        txt = round(self.modelElectrical.car2.energy_now.electrical,1)
        self.label_car2 = str(txt) + 'Wh'
        txt = round(self.modelElectrical.car2.energy_now.electrical,1)
        self.label_time = str(self.modelElectrical.time_current)
        txt = int(self.number_increment)
        self.label_increment = str(txt)

    def _update_labels_thermal(self):
        """
        Update the labels
        """
        txt = round(self.modelThermal1.provider.power.thermal, 1)
        self.label_radiator1_power = str(txt) + 'W'
        txt = round(self.modelThermal2.provider.power.thermal, 1)
        self.label_radiator2_power = str(txt) + 'W'
        txt = round(self.modelThermal3.provider.power.thermal, 1)
        self.label_radiator3_power = str(txt) + 'W'


    def callback_weather(self, *args):
        print("Show the weather forecast")

    def callback_photovoltaic(self, *args):
        print("Access the photovoltaic")
        print(self.modelElectrical.photovoltaic.energy_now.electrical)

    def callback_battery(self, *args):
        print("Access the battery")
        print(self.modelElectrical.battery.energy_now.electrical)

    def callback_car1(self, *args):
        print("Access the car")
        print(self.modelElectrical.car1.energy_now.electrical)

    def callback_car2(self, *args):
        print("Access the e-bicycle")
        print(self.modelElectrical.car2.energy_now.electrical)

    def callback_increment_do(self, *args):
        for i in range(self.number_increment):
            self.modelElectrical.increment()
        self._update_labels_electrical()
        print(self.modelElectrical.photovoltaic.energy_now.electrical)
        print(self.modelElectrical.battery.energy_now.electrical)
        Clock.schedule_once(self.callback_increment_do, 1)

    def callback_increment_slider(self, instance, value):
        self.number_increment = int(value)
        print(self.number_increment)

    def callback_increment_reset(self, *args):
        self.modelElectrical = ModelElectrical()
        self._update_labels_electrical()

    def callback_start_radiator_monitoring(self, *args):
        self.modelThermal1 = ModelThermal(room_power_out=10)
        self.modelThermal2 = ModelThermal(room_power_out=20)
        self.modelThermal3 = ModelThermal(room_power_out=100)

        # Check if model is already running then stop the old one
        if self.radiator_monitoring_running == False:
            self._callback_radiator_monitoring_do()
            self.radiator_monitoring_running = True
        # Wait for stop then call
        else:
            Clock.unschedule(self._callback_radiator_monitoring_do)
            self.radiator_monitoring_running = False
            self._callback_radiator_monitoring_do()
            self.radiator_monitoring_running = True


    def _callback_radiator_monitoring_do(self, *args):
        # Increment by some timesteps
        for i in range(10):
            self.modelThermal1.increment()
        if self.modelThermal1.threshold_counter > 150:
            if not self.modelThermal1.notification_sent:
                self.notificationRadiator.do_notify('Heizung 1')
                self.modelThermal1.notification_sent = True

        # Increment by some timesteps
        for i in range(10):
            self.modelThermal2.increment()
        if self.modelThermal2.threshold_counter > 150:
            if not self.modelThermal2.notification_sent:
                self.notificationRadiator.do_notify('Heizung 2')
                self.modelThermal2.notification_sent = True

        # Increment by some timesteps
        for i in range(10):
            self.modelThermal3.increment()
        if self.modelThermal3.threshold_counter > 150:
            if not self.modelThermal3.notification_sent:
                self.notificationRadiator.do_notify('Heizung 3')
                self.modelThermal3.notification_sent = True
        self._update_labels_thermal()

        Clock.schedule_once(self._callback_radiator_monitoring_do, 1)


class TerawattApp(App):

    def build(self):
        return Controller()


if __name__ == '__main__':
    TerawattApp().run()
