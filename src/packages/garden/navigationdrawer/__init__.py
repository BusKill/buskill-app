# Copyright (c) 2013 Alexander Taylor

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

'''NavigationDrawer
================

The NavigationDrawer widget provides a hidden panel view designed to
duplicate the popular Android layout.  The user views one main widget
but can slide from the left of the screen to view a second, previously
hidden widget. The transition between open/closed is smoothly
animated, with the parameters (anim time, panel width, touch
detection) all user configurable. If the panel is released without
being fully open or closed, it animates to an appropriate
configuration.

NavigationDrawer supports many different animation properties,
including moving one or both of the side/main panels, darkening
either/both widgets, changing side panel opacity, and changing which
widget is on top. The user can edit these individually to taste (this
is enough rope to hang oneself, it's easy to make a useless or silly
configuration!), or use one of a few preset animations.

The hidden panel might normally a set of navigation buttons, but the
implementation lets the user use any widget(s).

The first widget added to the NavigationDrawer is automatically used
as the side panel, and the second widget as the main panel. No further
widgets can be added, further changes are left to the user via editing
the panel widgets.

Usage summary
-------------

- The first widget added to a NavigationDrawer is used as the hidden
  side panel.
- The second widget added is used as the main panel.
- Both widgets can be removed with remove_widget, or alternatively
  set/removed with set_main_panel and set_side_panel.
- The hidden side panel can be revealed by dragging from the left of
  the NavigationDrawer. The touch detection width is the
  touch_accept_width property.
- Every animation property is user-editable, or default animations
  can be chosen by setting anim_type.

See the example and docstrings for information on individual properties.


Example::

class ExampleApp(App):

    def build(self):
        navigationdrawer = NavigationDrawer()

        side_panel = BoxLayout(orientation='vertical')
        side_panel.add_widget(Label(text='Panel label'))
        side_panel.add_widget(Button(text='A button'))
        side_panel.add_widget(Button(text='Another button'))
        navigationdrawer.add_widget(side_panel)

        label_head = (
            '[b]Example label filling main panel[/b]\n\n[color=ff0000](p'
            'ull from left to right!)[/color]\n\nIn this example, the le'
            'ft panel is a simple boxlayout menu, and this main panel is'
            ' a BoxLayout with a label and example image.\n\nSeveral pre'
            'set layouts are available (see buttons below), but users ma'
            'y edit every parameter for much more customisation.')
        main_panel = BoxLayout(orientation='vertical')
        label_bl = BoxLayout(orientation='horizontal')
        label = Label(text=label_head, font_size='15sp',
                      markup=True, valign='top')
        label_bl.add_widget(Widget(size_hint_x=None, width=dp(10)))
        label_bl.add_widget(label)
        label_bl.add_widget(Widget(size_hint_x=None, width=dp(10)))
        main_panel.add_widget(Widget(size_hint_y=None, height=dp(10)))
        main_panel.add_widget(label_bl)
        main_panel.add_widget(Widget(size_hint_y=None, height=dp(10)))
        navigationdrawer.add_widget(main_panel)
        label.bind(size=label.setter('text_size'))

        def set_anim_type(name):
            navigationdrawer.anim_type = name
        modes_layout = BoxLayout(orientation='horizontal')
        modes_layout.add_widget(Label(text='preset\nanims:'))
        slide_an = Button(text='slide_\nabove_\nanim')
        slide_an.bind(on_press=lambda j: set_anim_type('slide_above_anim'))
        slide_sim = Button(text='slide_\nabove_\nsimple')
        slide_sim.bind(on_press=lambda j: set_anim_type('slide_above_simple'))
        fade_in_button = Button(text='fade_in')
        fade_in_button.bind(on_press=lambda j: set_anim_type('fade_in'))
        reveal_button = Button(text='reveal_\nbelow_\nanim')
        reveal_button.bind(on_press=
                           lambda j: set_anim_type('reveal_below_anim'))
        slide_button = Button(text='reveal_\nbelow_\nsimple')
        slide_button.bind(on_press=
                          lambda j: set_anim_type('reveal_below_simple'))
        modes_layout.add_widget(slide_an)
        modes_layout.add_widget(slide_sim)
        modes_layout.add_widget(fade_in_button)
        modes_layout.add_widget(reveal_button)
        modes_layout.add_widget(slide_button)
        main_panel.add_widget(modes_layout)

        button = Button(text='toggle NavigationDrawer state (animate)',
                        size_hint_y=0.2)
        button.bind(on_press=lambda j: navigationdrawer.toggle_state())
        button2 = Button(text='toggle NavigationDrawer state (jump)',
                         size_hint_y=0.2)
        button2.bind(on_press=lambda j: navigationdrawer.toggle_state(False))
        button3 = Button(text='toggle _main_above', size_hint_y=0.2)
        button3.bind(on_press=navigationdrawer.toggle_main_above)
        main_panel.add_widget(button)
        main_panel.add_widget(button2)
        main_panel.add_widget(button3)

        return navigationdrawer

    ExampleApp().run()

'''

__all__ = ('NavigationDrawer', )

from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.uix.stencilview import StencilView
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import (ObjectProperty, NumericProperty, OptionProperty,
                             BooleanProperty, StringProperty)
from kivy.resources import resource_add_path
from kivy.lang import Builder
import os.path

resource_add_path(os.path.dirname(__file__))

Builder.load_string('''
<NavigationDrawer>:
    size_hint: (1,1)
    _side_panel: sidepanel
    _main_panel: mainpanel
    _join_image: joinimage
    side_panel_width: min(dp(250), 0.5*self.width)
    BoxLayout:
        id: sidepanel
        y: root.y
        x: root.x - \
           (1-root._anim_progress)* \
           root.side_panel_init_offset*root.side_panel_width
        height: root.height
        width: root.side_panel_width
        opacity: root.side_panel_opacity + \
                 (1-root.side_panel_opacity)*root._anim_progress
        canvas:
            Color:
                #rgba: (0,0,0,1)
                # https://github.com/kivy-garden/garden.navigationdrawer/issues/12
                rgba: (0.259,0.259,0.259,1)
            Rectangle:
                pos: self.pos
                size: self.size
        canvas.after:
            Color:
                rgba: (1,0,0,(1-root._anim_progress)*root.side_panel_darkness)
            Rectangle:
                size: self.size
                pos: self.pos
    BoxLayout:
        id: mainpanel
        x: root.x + \
           root._anim_progress * \
           root.side_panel_width * \
           root.main_panel_final_offset
        y: root.y
        size: root.size
        canvas:
            Color:
                #rgba: (0,0,0,1)
                # https://github.com/kivy-garden/garden.navigationdrawer/issues/12
                rgba: (0.188,0.188,0.188,1)
            Rectangle:
                pos: self.pos
                size: self.size
        canvas.after:
            Color:
                rgba: (0,0,0,root._anim_progress*root.main_panel_darkness)
            Rectangle:
                size: self.size
                pos: self.pos
    Image:
        id: joinimage
        opacity: min(sidepanel.opacity, 0 if root._anim_progress < 0.00001 \
                 else min(root._anim_progress*40,1))
        source: root._choose_image(root._main_above, root.separator_image)
        mipmap: False
        width: root.separator_image_width
        height: root._side_panel.height
        x: (mainpanel.x - self.width + 1) if root._main_above \
           else (sidepanel.x + sidepanel.width - 1)
        y: root.y
        allow_stretch: True
        keep_ratio: False
''')


class NavigationDrawerException(Exception):
    '''Raised when add_widget or remove_widget called incorrectly on a
    NavigationDrawer.

    '''


class NavigationDrawer(StencilView):
    '''Widget taking two children, a side panel and a main panel,
    displaying them in a way that replicates the popular Android
    functionality. See module documentation for more info.

    '''

    # Internal references for side, main and image widgets
    _side_panel = ObjectProperty()
    _main_panel = ObjectProperty()
    _join_image = ObjectProperty()

    side_panel = ObjectProperty(None, allownone=True)
    '''Automatically bound to whatever widget is added as the hidden panel.'''
    main_panel = ObjectProperty(None, allownone=True)
    '''Automatically bound to whatever widget is added as the main panel.'''

    # Appearance properties
    side_panel_width = NumericProperty()
    '''The width of the hidden side panel. Defaults to the minimum of
    250dp or half the NavigationDrawer width.'''
    separator_image = StringProperty('')
    '''The path to an image that will be placed between the side and main
    panels. If set to `''`, defaults to a gradient from black to
    transparent in an appropriate direction (left->right if side panel
    above main, right->left if main panel on top).'''
    separator_image_width = NumericProperty(dp(10))
    '''The width of the separator image. Defaults to 10dp'''

    # Touch properties
    touch_accept_width = NumericProperty('14dp')
    '''Distance from the left of the NavigationDrawer in which to grab the
    touch and allow revealing of the hidden panel.'''
    _touch = ObjectProperty(None, allownone=True)  # The currently active touch

    # Animation properties
    state = OptionProperty('closed', options=('open', 'closed'))
    '''Specifies the state of the widget. Must be one of 'open' or
    'closed'. Setting its value automatically jumps to the relevant state,
    or users may use the anim_to_state() method to animate the
    transition.'''
    anim_time = NumericProperty(0.3)
    '''The time taken for the panel to slide to the open/closed state when
    released or manually animated with anim_to_state.'''
    min_dist_to_open = NumericProperty(0.7)
    '''Must be between 0 and 1. Specifies the fraction of the hidden panel
    width beyond which the NavigationDrawer will relax to open state when
    released. Defaults to 0.7.'''
    _anim_progress = NumericProperty(0)  # Internal state controlling
                                         # widget positions
    _anim_init_progress = NumericProperty(0)

    # Animation controls
    top_panel = OptionProperty('main', options=['main', 'side'])
    '''Denotes which panel should be drawn on top of the other. Must be
    one of 'main' or 'side'. Defaults to 'main'.'''
    _main_above = BooleanProperty(True)

    side_panel_init_offset = NumericProperty(0.5)
    '''Intial offset (to the left of the widget) of the side panel, in
    units of its total width. Opening the panel moves it smoothly to its
    final position at the left of the screen.'''

    side_panel_darkness = NumericProperty(0.8)
    '''Controls the fade-to-black of the side panel in its hidden
    state. Must be between 0 (no fading) and 1 (fades to totally
    black).'''

    side_panel_opacity = NumericProperty(1)
    '''Controls the opacity of the side panel in its hidden state. Must be
    between 0 (fade to transparent) and 1 (no transparency)'''

    main_panel_final_offset = NumericProperty(1)
    '''Final offset (to the right of the normal position) of the main
    panel, in units of the side panel width.'''

    main_panel_darkness = NumericProperty(0)
    '''Controls the fade-to-black of the main panel when the side panel is
    in its hidden state. Must be between 0 (no fading) and 1 (fades to
    totally black).
    '''

    opening_transition = StringProperty('out_cubic')
    '''The name of the animation transition type to use when animating to
    an open state. Defaults to 'out_cubic'.'''

    closing_transition = StringProperty('in_cubic')
    '''The name of the animation transition type to use when animating to
    a closed state. Defaults to 'out_cubic'.'''

    anim_type = OptionProperty('reveal_from_below',
                               options=['slide_above_anim',
                                        'slide_above_simple',
                                        'fade_in',
                                        'reveal_below_anim',
                                        'reveal_below_simple',
                                        ])
    '''The default animation type to use. Several options are available,
    modifying all possibly animation properties including darkness,
    opacity, movement and draw height. Users may also (and are
    encouaged to) edit these properties individually, for a vastly
    larger range of possible animations. Defaults to reveal_below_anim.
    '''

    def __init__(self, **kwargs):
        super(NavigationDrawer, self).__init__(**kwargs)
        Clock.schedule_once(self.on__main_above, 0)

    def on_anim_type(self, *args):
        anim_type = self.anim_type
        if anim_type == 'slide_above_anim':
            self.top_panel = 'side'
            self.side_panel_darkness = 0
            self.side_panel_opacity = 1
            self.main_panel_final_offset = 0.5
            self.main_panel_darkness = 0.5
            self.side_panel_init_offset = 1
        if anim_type == 'slide_above_simple':
            self.top_panel = 'side'
            self.side_panel_darkness = 0
            self.side_panel_opacity = 1
            self.main_panel_final_offset = 0
            self.main_panel_darkness = 0
            self.side_panel_init_offset = 1
        elif anim_type == 'fade_in':
            self.top_panel = 'side'
            self.side_panel_darkness = 0
            self.side_panel_opacity = 0
            self.main_panel_final_offset = 0
            self.main_panel_darkness = 0
            self.side_panel_init_offset = 0.5
        elif anim_type == 'reveal_below_anim':
            self.top_panel = 'main'
            self.side_panel_darkness = 0.8
            self.side_panel_opacity = 1
            self.main_panel_final_offset = 1
            self.main_panel_darkness = 0
            self.side_panel_init_offset = 0.5
        elif anim_type == 'reveal_below_simple':
            self.top_panel = 'main'
            self.side_panel_darkness = 0
            self.side_panel_opacity = 1
            self.main_panel_final_offset = 1
            self.main_panel_darkness = 0
            self.side_panel_init_offset = 0

    def on_top_panel(self, *args):
        if self.top_panel == 'main':
            self._main_above = True
        else:
            self._main_above = False

    def on__main_above(self, *args):
        newval = self._main_above
        main_panel = self._main_panel
        side_panel = self._side_panel
        self.canvas.remove(main_panel.canvas)
        self.canvas.remove(side_panel.canvas)
        if newval:
            self.canvas.insert(0, main_panel.canvas)
            self.canvas.insert(0, side_panel.canvas)
        else:
            self.canvas.insert(0, side_panel.canvas)
            self.canvas.insert(0, main_panel.canvas)

    def toggle_main_above(self, *args):
        if self._main_above:
            self._main_above = False
        else:
            self._main_above = True

    def add_widget(self, widget):
        if len(self.children) == 0:
            super(NavigationDrawer, self).add_widget(widget)
            self._side_panel = widget
        elif len(self.children) == 1:
            super(NavigationDrawer, self).add_widget(widget)
            self._main_panel = widget
        elif len(self.children) == 2:
            super(NavigationDrawer, self).add_widget(widget)
            self._join_image = widget
        elif self.side_panel is None:
            self._side_panel.add_widget(widget)
            self.side_panel = widget
        elif self.main_panel is None:
            self._main_panel.add_widget(widget)
            self.main_panel = widget
        else:
            raise NavigationDrawerException(
                'Can\'t add more than two widgets'
                'directly to NavigationDrawer')

    def remove_widget(self, widget):
        if widget is self.side_panel:
            self._side_panel.remove_widget(widget)
            self.side_panel = None
        elif widget is self.main_panel:
            self._main_panel.remove_widget(widget)
            self.main_panel = None
        else:
            raise NavigationDrawerException(
                'Widget is neither the side or main panel, can\'t remove it.')

    def set_side_panel(self, widget):
        '''Removes any existing side panel widgets, and replaces them with the
        argument `widget`.
        '''
        # Clear existing side panel entries
        if len(self._side_panel.children) > 0:
            for child in self._side_panel.children:
                self._side_panel.remove(child)
        # Set new side panel
        self._side_panel.add_widget(widget)
        self.side_panel = widget

    def set_main_panel(self, widget):
        '''Removes any existing main panel widgets, and replaces them with the
        argument `widget`.
        '''
        # Clear existing side panel entries
        if len(self._main_panel.children) > 0:
            for child in self._main_panel.children:
                self._main_panel.remove_widget(child)
        # Set new side panel
        self._main_panel.add_widget(widget)
        self.main_panel = widget

    def on__anim_progress(self, *args):
        if self._anim_progress > 1:
            self._anim_progress = 1
        elif self._anim_progress < 0:
            self._anim_progress = 0
        if self._anim_progress >= 1:
            self.state = 'open'
        elif self._anim_progress <= 0:
            self.state = 'closed'

    def on_state(self, *args):
        Animation.cancel_all(self)
        if self.state == 'open':
            self._anim_progress = 1
        else:
            self._anim_progress = 0

    def anim_to_state(self, state):
        '''If not already in state `state`, animates smoothly to it, taking
        the time given by self.anim_time. State may be either 'open'
        or 'closed'.

        '''
        if state == 'open':
            anim = Animation(_anim_progress=1,
                             duration=self.anim_time,
                             t=self.closing_transition)
            anim.start(self)
        elif state == 'closed':
            anim = Animation(_anim_progress=0,
                             duration=self.anim_time,
                             t=self.opening_transition)
            anim.start(self)
        else:
            raise NavigationDrawerException(
                'Invalid state received, should be one of `open` or `closed`')

    def toggle_state(self, animate=True):
        '''Toggles from open to closed or vice versa, optionally animating or
        simply jumping.'''
        if self.state == 'open':
            if animate:
                self.anim_to_state('closed')
            else:
                self.state = 'closed'
        elif self.state == 'closed':
            if animate:
                self.anim_to_state('open')
            else:
                self.state = 'open'

    def on_touch_down(self, touch):
        col_self = self.collide_point(*touch.pos)
        col_side = self._side_panel.collide_point(*touch.pos)
        col_main = self._main_panel.collide_point(*touch.pos)

        if self._anim_progress < 0.001:  # i.e. closed
            valid_region = (self.x <=
                            touch.x <=
                            (self.x + self.touch_accept_width))
            if not valid_region:
                self._main_panel.on_touch_down(touch)
                return False
        else:
            if col_side and not self._main_above:
                self._side_panel.on_touch_down(touch)
                return False
            valid_region = (self._main_panel.x <=
                            touch.x <=
                            (self._main_panel.x + self._main_panel.width))
            if not valid_region:
                if self._main_above:
                    if col_main:
                        self._main_panel.on_touch_down(touch)
                    elif col_side:
                        self._side_panel.on_touch_down(touch)
                else:
                    if col_side:
                        self._side_panel.on_touch_down(touch)
                    elif col_main:
                        self._main_panel.on_touch_down(touch)
                return False
        Animation.cancel_all(self)
        self._anim_init_progress = self._anim_progress
        self._touch = touch
        touch.ud['type'] = self.state
        touch.ud['panels_jiggled'] = False  # If user moved panels back
                                            # and forth, don't default
                                            # to close on touch release
        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        if touch is self._touch:
            dx = touch.x - touch.ox
            self._anim_progress = max(0, min(self._anim_init_progress +
                                            (dx / self.side_panel_width), 1))
            if self._anim_progress < 0.975:
                touch.ud['panels_jiggled'] = True
        else:
            super(NavigationDrawer, self).on_touch_move(touch)
            return

    def on_touch_up(self, touch):
        if touch is self._touch:
            self._touch = None
            init_state = touch.ud['type']
            touch.ungrab(self)
            jiggled = touch.ud['panels_jiggled']
            if init_state == 'open' and not jiggled:
                if self._anim_progress >= 0.975:
                        self.anim_to_state('closed')
                else:
                    self._anim_relax()
            else:
                self._anim_relax()
        else:
            super(NavigationDrawer, self).on_touch_up(touch)
            return

    def _anim_relax(self):
        '''Animates to the open or closed position, depending on whether the
        current position is past self.min_dist_to_open.

        '''
        if self._anim_progress > self.min_dist_to_open:
            self.anim_to_state('open')
        else:
            self.anim_to_state('closed')

    def _choose_image(self, *args):
        '''Chooses which image to display as the main/side separator, based on
        _main_above.'''
        if self.separator_image:
            return self.separator_image
        if self._main_above:
            return 'navigationdrawer_gradient_rtol.png'
        else:
            return 'navigationdrawer_gradient_ltor.png'

if __name__ == '__main__':
    from kivy.base import runTouchApp
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.popup import Popup
    from kivy.uix.image import Image
    from kivy.core.window import Window

    navigationdrawer = NavigationDrawer()

    side_panel = BoxLayout(orientation='vertical')
    side_panel.add_widget(Label(text='Panel label'))
    popup = Popup(title='Sidebar popup',
                  content=Label(
                      text='You clicked the sidebar\npopup button'),
                  size_hint=(0.7, 0.7))
    first_button = Button(text='Popup\nbutton')
    first_button.bind(on_release=popup.open)
    side_panel.add_widget(first_button)
    side_panel.add_widget(Button(text='Another\nbutton'))
    navigationdrawer.add_widget(side_panel)

    label_head = (
        '[b]Example label filling main panel[/b]\n\n[color=ff0000](p'
        'ull from left to right!)[/color]\n\nIn this example, the le'
        'ft panel is a simple boxlayout menu, and this main panel is'
        ' a BoxLayout with a label and example image.\n\nSeveral pre'
        'set layouts are available (see buttons below), but users ma'
        'y edit every parameter for much more customisation.')
    main_panel = BoxLayout(orientation='vertical')
    label_bl = BoxLayout(orientation='horizontal')
    label = Label(text=label_head, font_size='15sp',
                  markup=True, valign='top')
    label_bl.add_widget(Widget(size_hint_x=None, width=dp(10)))
    label_bl.add_widget(label)
    label_bl.add_widget(Widget(size_hint_x=None, width=dp(10)))
    main_panel.add_widget(Widget(size_hint_y=None, height=dp(10)))
    main_panel.add_widget(label_bl)
    main_panel.add_widget(Widget(size_hint_y=None, height=dp(10)))
    navigationdrawer.add_widget(main_panel)
    label.bind(size=label.setter('text_size'))

    def set_anim_type(name):
        navigationdrawer.anim_type = name

    def set_transition(name):
        navigationdrawer.opening_transition = name
        navigationdrawer.closing_transition = name

    modes_layout = BoxLayout(orientation='horizontal')
    modes_layout.add_widget(Label(text='preset\nanims:'))
    slide_an = Button(text='slide_\nabove_\nanim')
    slide_an.bind(on_press=lambda j: set_anim_type('slide_above_anim'))
    slide_sim = Button(text='slide_\nabove_\nsimple')
    slide_sim.bind(on_press=lambda j: set_anim_type('slide_above_simple'))
    fade_in_button = Button(text='fade_in')
    fade_in_button.bind(on_press=lambda j: set_anim_type('fade_in'))
    reveal_button = Button(text='reveal_\nbelow_\nanim')
    reveal_button.bind(on_press=
                       lambda j: set_anim_type('reveal_below_anim'))
    slide_button = Button(text='reveal_\nbelow_\nsimple')
    slide_button.bind(on_press=
                      lambda j: set_anim_type('reveal_below_simple'))
    modes_layout.add_widget(slide_an)
    modes_layout.add_widget(slide_sim)
    modes_layout.add_widget(fade_in_button)
    modes_layout.add_widget(reveal_button)
    modes_layout.add_widget(slide_button)
    main_panel.add_widget(modes_layout)

    transitions_layout = BoxLayout(orientation='horizontal')
    transitions_layout.add_widget(Label(text='anim\ntransitions'))
    out_cubic = Button(text='out_cubic')
    out_cubic.bind(on_press=
                   lambda j: set_transition('out_cubic'))
    in_quint = Button(text='in_quint')
    in_quint.bind(on_press=
                  lambda j: set_transition('in_quint'))
    linear = Button(text='linear')
    linear.bind(on_press=
                lambda j: set_transition('linear'))
    out_sine = Button(text='out_sine')
    out_sine.bind(on_press=
                  lambda j: set_transition('out_sine'))
    transitions_layout.add_widget(out_cubic)
    transitions_layout.add_widget(in_quint)
    transitions_layout.add_widget(linear)
    transitions_layout.add_widget(out_sine)
    main_panel.add_widget(transitions_layout)

    button = Button(text='toggle NavigationDrawer state (animate)',
                    size_hint_y=0.2)
    button.bind(on_press=lambda j: navigationdrawer.toggle_state())
    button2 = Button(text='toggle NavigationDrawer state (jump)',
                     size_hint_y=0.2)
    button2.bind(on_press=lambda j: navigationdrawer.toggle_state(False))
    button3 = Button(text='toggle _main_above', size_hint_y=0.2)
    button3.bind(on_press=navigationdrawer.toggle_main_above)
    main_panel.add_widget(button)
    main_panel.add_widget(button2)
    main_panel.add_widget(button3)

    Window.add_widget(navigationdrawer)

    runTouchApp()
