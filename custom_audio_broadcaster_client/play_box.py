import gi
from gstreamer_pipeline import GstreamerPipeline
from logger import logger

gi.require_version('Gtk', '4.0')

from gi.repository import Gtk  # type: ignore

PLAY_ICON = 'media-playback-start-symbolic'
PAUSE_ICON = 'media-playback-pause-symbolic'


class PlayBox(Gtk.Box):

  def __init__(self, pipeline: GstreamerPipeline):
    super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
    self.pipeline = pipeline
    # Play button
    play_button = Gtk.Button()
    play_button.set_icon_name(PLAY_ICON)
    play_button.set_css_classes(['flat', 'circular'])
    play_button.connect('clicked', self.on_button_clicked)
    self.append(play_button)

    # Visualizer
    visualizer = Gtk.Picture.new()
    visualizer.add_css_class('visualizer')
    visualizer.set_size_request(100, 32)
    self.pipeline.set_vis_size(100, 32)
    visualizer.set_paintable(self.pipeline.paintable)

    self.revealer = Gtk.Revealer(
        transition_type=Gtk.RevealerTransitionType.SLIDE_RIGHT,
        transition_duration=500,
        child=visualizer,
        reveal_child=False,
    )
    self.append(self.revealer)

  def on_button_clicked(self, button):
    self.pipeline.toggle_state()
    self.revealer.set_reveal_child(not self.revealer.get_reveal_child())
    logger.info('Playing audio...' if self.pipeline.is_playing(
    ) else 'Pausing audio...')
    if button.get_icon_name() == PLAY_ICON:
      button.set_icon_name(PAUSE_ICON)
    else:
      button.set_icon_name(PLAY_ICON)
