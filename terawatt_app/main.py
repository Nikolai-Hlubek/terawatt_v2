from kivy.app import App
from kivy.uix.pagelayout import PageLayout

from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.vector import Vector


class CircularButton(ButtonBehavior, Widget):
	def collide_point(self, x, y):
		return Vector(x, y).distance(self.center) <= self.width / 2

		
class MainLayout(PageLayout):
	pass


class TerawattApp(App):

    def build(self):
        return MainLayout()

def callback(*args):
	print "i'm being pressed"
		

if __name__ == '__main__':
    TerawattApp().run()

	




      runTouchApp(CircularButton(on_press=callback))
