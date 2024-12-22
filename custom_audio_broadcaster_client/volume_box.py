import gi
from gstreamer_pipeline import GstreamerPipeline
from typing import Optional

gi.require_version('Gtk', '4.0')

from gi.repository import Gtk  # type: ignore

UNMUTED_ICON = 'audio-volume-high-symbolic'
MUTED_ICON = 'audio-volume-muted-symbolic'


class VolumeBox(Gtk.Box):

  def __init__(self, pipeline: GstreamerPipeline):
    super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
    self.pipeline = pipeline
    self.timeout_id: Optional[int] = None

    mute_button = Gtk.Button()
    mute_button.set_icon_name(UNMUTED_ICON)
    mute_button.set_css_classes(['flat', 'circular'])
    mute_button.connect('clicked', self.on_button_clicked)
    self.append(mute_button)
    mute_button_hover_controller = Gtk.EventControllerMotion()
    mute_button_hover_controller.connect('enter', self.on_enter)
    mute_button_hover_controller.connect('leave', self.on_leave)
    mute_button.add_controller(mute_button_hover_controller)

    volume_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1,
                                            0.01)
    volume_scale.set_size_request(100, -1)
    volume_scale.set_value(0.5)
    volume_scale.connect(
        'value-changed',
        lambda scale: self.pipeline.set_volume(scale.get_value()))
    volume_scale_hover_controller = Gtk.EventControllerMotion()
    volume_scale_hover_controller.connect('enter', self.on_enter)
    volume_scale_hover_controller.connect('leave', self.on_leave)
    volume_scale.add_controller(volume_scale_hover_controller)
    self.revealer = Gtk.Revealer(
        transition_type=Gtk.RevealerTransitionType.SLIDE_RIGHT,
        transition_duration=500,
        child=volume_scale,
        reveal_child=False,
    )
    self.append(self.revealer)

  def on_button_clicked(self, button):
    self.pipeline.toggle_mute()
    if button.get_icon_name() == MUTED_ICON:
      button.set_icon_name(UNMUTED_ICON)
    else:
      button.set_icon_name(MUTED_ICON)

  def on_enter(self, controller, x, y):
    self.revealer.set_reveal_child(True)

  def on_leave(self, controller):
    self.revealer.set_reveal_child(False)
