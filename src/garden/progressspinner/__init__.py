'''
ProgressSpinner
===============

Android Lollipop style progress spinner.
'''

from kivy.lang import Builder
from kivy.core.image import Image as CoreImage
from kivy.properties import NumericProperty, ListProperty, BoundedNumericProperty, StringProperty, ObjectProperty
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import BooleanProperty
from kivy.uix.widget import Widget

Builder.load_string('''
<ProgressSpinnerBase>:
	_size: min(self.height, self.width)
	_rsize: self._size / 2.
	_stroke: max(0.1, self._rsize / 20. if self.stroke_width is None else self.stroke_width)
	_radius: self._rsize - self._stroke * 2.

<ProgressSpinner>:
	canvas:
		Color:
			rgba: self.color
		Line:
			circle:
				(self.center_x, self.center_y, self._radius,
				self._angle_center + self._angle_start,
				self._angle_center + self._angle_end)
			width: self._stroke
			cap: 'none'

<TextureProgressSpinner>:
	canvas:
		StencilPush
		Color:
			rgba: 1, 1, 1, 1
		Line:
			circle:
				(self.center_x, self.center_y, self._radius,
				self._angle_center + self._angle_start,
				self._angle_center + self._angle_end)
			width: self._stroke
			cap: 'none'
		StencilUse

		Color:
			rgba: self.color
		Rectangle:
			pos: self.center_x - self._rsize, self.center_y - self._rsize
			size: self._size, self._size
			texture: self.texture

		StencilUnUse
		Color:
			rgba: 1, 1, 1, 1
		Line:
			circle:
				(self.center_x, self.center_y, self._radius,
				self._angle_center + self._angle_start,
				self._angle_center + self._angle_end)
			width: self._stroke
			cap: 'none'
		StencilPop

<RotatingTextureProgressSpinner>:
	canvas:
		PushMatrix
		Rotate:
			angle: -self._angle_center
			origin: self.center
		
		StencilPush
		Color:
			rgba: 1, 1, 1, 1
		Line:
			circle:
				(self.center_x, self.center_y, self._radius,
				self._angle_start, self._angle_end)
			width: self._stroke
			cap: 'none'
		StencilUse

		Color:
			rgba: self.color
		Rectangle:
			pos: self.center_x - self._rsize, self.center_y - self._rsize
			size: self._size, self._size
			texture: self.texture

		StencilUnUse
		Color:
			rgba: 1, 1, 1, 1
		Line:
			circle:
				(self.center_x, self.center_y, self._radius,
				self._angle_start, self._angle_end)
			width: self._stroke
			cap: 'none'
		StencilPop
		
		PopMatrix

''')


class ProgressSpinnerBase(Widget):
    '''ProgressSpinnerBase - base class for progress spinner widgets
    '''

    color = ListProperty([1, 1, 1, 1])
    '''Color to render the spinner.

    :attr:`color` is a :class:`~kivy.properties.ListProperty` and defaults
    to [1, 1, 1, 1] (white, full opacity).
    '''

    speed = BoundedNumericProperty(1, min=0.1)
    '''Speed coefficient of the spinner. This value is multiplied by the
    base speed of 90 degrees per second.

    :attr:`speed` is a :class:`~kivy.properties.BoundedNumericProperty` and
    defaults to 1.
    '''

    stroke_length = BoundedNumericProperty(25., min=1, max=180)
    '''Base length of the stroke in degrees.

    :attr:`stroke_length` is a :class:`~kivy.properties.BoundedNumericProperty`
    and defaults to 25.
    '''

    stroke_width = NumericProperty(None, allownone=True)
    '''Width of the stroke in pixels. If set to None, the width will be
    calculated automatically as 1/20th of the radius.

    :attr:`stroke_width` is a :class:`~kivy.properties.NumericProperty` and
    defaults to None.
    '''

    auto_start = BooleanProperty(True)
    '''Whether to automatically start spinning.

    :attr:`auto_start` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to True.
    '''

    # internal properties
    _angle_center = NumericProperty(0)
    _angle_start = NumericProperty()
    _angle_end = NumericProperty()
    _size = NumericProperty()
    _rsize = NumericProperty()
    _stroke = NumericProperty(1)
    _radius = NumericProperty(50)

    def __init__(self, **kwargs):
        super(ProgressSpinnerBase, self).__init__(**kwargs)
        self._state = 'wait1'
        self._next = None
        self._spinning = False

        if self.auto_start:
            self.start_spinning()

    def start_spinning(self, *args):
        '''Start spinning the progress spinner. Ignores all positional args
        for easy binding.
        '''
        if not self._spinning:
            self._state = 'wait1'
            self._next = None
            self._angle_center = 0.
            self._angle_start = 360.
            self._angle_end = 360. + self.stroke_length
            Clock.schedule_interval(self._update, 0)
            Clock.schedule_once(self._rotate, 0.3)
            self._spinning = True

    def stop_spinning(self, *args):
        '''Stop spinning the progress spinner. Ignores all positional args
        for easy binding.

        If you intend to keep the spinner around, you should stop it when
        not using it and restart it when needed again.
        '''
        if self._spinning:
            if self._next:
                if isinstance(self._next, Animation):
                    self._next.cancel(self)
                else:
                    self._next.cancel()
            Clock.unschedule(self._update)
            Clock.unschedule(self._rotate)
            self._angle_start = self._angle_end = 0
            self._spinning = False

    def _update(self, dt):
        angle_speed = 90. * self.speed
        self._angle_center += dt * angle_speed

        if self._angle_center > 360:
            self._angle_center -= 360.

    def _rotate(self, *args):
        if not self._spinning:
            return

        rotate_speed = 0.6 / self.speed
        wait_speed = 0.3 / self.speed
        if self._state == 'wait1':
            self._state = 'rotate1'
            self._next = Animation(_angle_end=self._angle_start + 360. - self.stroke_length, d=rotate_speed,
                                   t='in_quad')
            self._next.bind(on_complete=self._rotate)
            self._next.start(self)
        elif self._state == 'rotate1':
            self._state = 'wait2'
            self._next = Clock.schedule_once(self._rotate, wait_speed)
        elif self._state == 'wait2':
            self._state = 'rotate2'
            self._next = Animation(_angle_start=self._angle_end - self.stroke_length, d=rotate_speed, t='in_quad')
            self._next.bind(on_complete=self._rotate)
            self._next.start(self)
        elif self._state == 'rotate2':
            self._state = 'wait1'
            self._next = Clock.schedule_once(self._rotate, wait_speed)
            while self._angle_end > 720.:
                self._angle_start -= 360.
                self._angle_end -= 360.


class ProgressSpinner(ProgressSpinnerBase):
    '''ProgressSpinner class. Android Lollipop style progress spinner.
    '''
    pass


class TextureProgressSpinnerBase(ProgressSpinnerBase):
    texture = ObjectProperty()
    '''Texture to render for the spinner.

    :attr:`texture` is a :class:`~kivy.properties.ObjectProperty` and
    defaults to None.
    '''

    source = StringProperty('')
    '''Source image to render for the spinner.

    :attr:`source` is a :class:`~kivy.properties.StringProperty` and
    defaults to an empty string.
    '''

    def on_source(self, inst, value):
        if value:
            self.texture = CoreImage(value).texture


class TextureProgressSpinner(TextureProgressSpinnerBase):
    '''TextureProgressSpinner class.

    Same as ProgressSpinner, but with a texture/image instead of a solid color.
    '''
    pass


class RotatingTextureProgressSpinner(TextureProgressSpinnerBase):
    '''RotatingTextureProgressSpinner class.

    Same as TextureProgressSpinner, but the texture/image rotates along with
    the spinner.
    '''
    pass


if __name__ == '__main__':
    from kivy.app import App
    from kivy.graphics.texture import Texture
    from textwrap import dedent


    class TestApp(App):
        texture = ObjectProperty()

        def blittex(self, *args):
            rgbpixels = [(x, 0, y, 255) for x in range(256) for y in range(256)]
            pixels = b''.join((b''.join(map(bytearray, pix)) for pix in rgbpixels))
            self.texture = Texture.create(size=(256, 256))
            self.texture.blit_buffer(pixels, colorfmt='rgba', bufferfmt='ubyte')

        def build(self):
            Clock.schedule_once(self.blittex, -1)

            return Builder.load_string(dedent('''\
				<ProgressSpinnerBase>:
					on_touch_down: self.stop_spinning() if self._spinning else self.start_spinning()

				<TTextureProgressSpinner@TextureProgressSpinner>:
					texture: app.texture

				<TRotatingTextureProgressSpinner@RotatingTextureProgressSpinner>:
					texture: app.texture
				
				<ITextureProgressSpinner@TextureProgressSpinner>:
					source: 'demoimage.jpg'
				
				<IRotatingTextureProgressSpinner@RotatingTextureProgressSpinner>:
					source: 'demoimage.jpg'

				BoxLayout:
					BoxLayout:
						orientation: 'vertical'
						
						ProgressSpinner
						
						TTextureProgressSpinner
						
						TRotatingTextureProgressSpinner
					
					BoxLayout:
						orientation: 'vertical'
						
						BoxLayout:
							ProgressSpinner:
								color: 0.3, 0.3, 1, 1
								stroke_width: 1
							
							ProgressSpinner:
								speed: 0.5
								color: 1, 0, 0, 1
							
							ProgressSpinner:
								speed: 2
								color: 0, 1, 0, 1
						
						BoxLayout:
							TTextureProgressSpinner:
								color: 1, 0, 0, 1
							
							ITextureProgressSpinner:
								stroke_width: 10
							
							ITextureProgressSpinner:
								stroke_length: 20
								
						BoxLayout:
							TRotatingTextureProgressSpinner:
								color: 1, 0, 0, 1
							
							IRotatingTextureProgressSpinner:
								stroke_width: 10
							
							IRotatingTextureProgressSpinner:
								stroke_length: 20
			'''))


    TestApp().run()
