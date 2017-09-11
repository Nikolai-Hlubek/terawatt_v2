from kivy.app import App
from kivy.uix.pagelayout import PageLayout


class Controller(PageLayout):

    def callback_weather(*args):
        print("Show the weather forecast")

    def callback_photovoltaic(*args):
        print("Access the photovoltaic")

    def callback_battery(*args):
        print("Access the battery")

    def callback_car(*args):
        print("Access the car")


class TerawattApp(App):

    def build(self):
        return Controller()


if __name__ == '__main__':
    TerawattApp().run()
