import sys
import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst  # type: ignore


class GstreamerPipeline:

  def __init__(self, uri: str, width=480, height=480):
    Gst.init(sys.argv[1:])
    self.uri = uri
    self.pipeline = Gst.parse_launch(f'playbin uri="{self.uri}"')

    self.pipeline.props.flags |= 1 << 3
    vis = Gst.ElementFactory.make('spectrascope', 'vis')
    self.pipeline.set_property('vis-plugin', vis)
    gtksink = Gst.ElementFactory.make('gtk4paintablesink', 'sink')
    self.pipeline.set_property('video-sink', gtksink)
    self.set_vis_size(width, height)
    self.paintable = gtksink.props.paintable

  def is_playing(self) -> bool:
    return self.pipeline.get_state(1)[1] == Gst.State.PLAYING

  def toggle_state(self):
    if self.is_playing():
      self.pipeline.set_state(Gst.State.PAUSED)
    else:
      self.pipeline.set_state(Gst.State.PLAYING)

  def is_muted(self) -> bool:
    return self.pipeline.get_property('mute')

  def toggle_mute(self):
    if self.is_muted():
      self.pipeline.set_property('mute', False)
    else:
      self.pipeline.set_property('mute', True)

  def set_volume(self, volume: float):
    self.pipeline.set_property('volume', volume)

  def set_vis_size(self, width: int, height: int):
    video_caps = Gst.Caps.from_string(
        f'video/x-raw,width={width},height={height}')
    caps_filter = Gst.ElementFactory.make('capsfilter', 'capsfilter')
    caps_filter.set_property('caps', video_caps)
    self.pipeline.set_property('video-filter', caps_filter)

  def set_uri(self, uri: str):
    self.pipeline.set_property('uri', uri)
