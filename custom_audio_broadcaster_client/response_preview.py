import re
import gi
import json

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk  # type: ignore

json_keys_regex = r'(\".*?\")(?=:)'
json_string_values_regex = r'(?<=:\s)(\".*?\")'
json_non_string_values_regex = r'(?<=:\s)([0-9]+|null|true|false)'


class ResponsePreview(Gtk.ScrolledWindow):

  def __init__(self, json_str: str):
    super().__init__(vexpand=True)
    self.text_view = Gtk.TextView(editable=False, cursor_visible=False)
    self.add_css_class('response-preview')
    self.set_child(self.text_view)
    self.set_str(json_str)

  def set_str(self, parsed_json):
    json_str = json.dumps(parsed_json, indent=2)
    buffer = self.text_view.get_buffer()
    if not json_str or buffer.get_text(
        buffer.get_start_iter(), buffer.get_end_iter(), True) == json_str:
      return
    json_str = re.sub(r'&', '&amp;', json_str)
    json_str = re.sub(json_keys_regex, r'<span foreground="#8aadf4">\1</span>',
                      json_str)
    json_str = re.sub(json_string_values_regex,
                      r'<span foreground="#a6da95">\1</span>', json_str)
    json_str = re.sub(json_non_string_values_regex,
                      r'<span foreground="#f5a97f">\1</span>', json_str)
    buffer = self.text_view.get_buffer()
    self.buffer = buffer
    self.buffer.set_text('')
    self.buffer.insert_markup(self.buffer.get_end_iter(), json_str, -1)
