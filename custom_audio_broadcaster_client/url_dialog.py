import gi
from typing import Callable, Optional
from tweak_titlebar import tweak_titlebar

gi.require_version('Gtk', '4.0')

from gi.repository import Gtk  # type: ignore


class UrlDialog(Gtk.ApplicationWindow):

  def __init__(self,
               placeholder: str = 'http://localhost:3000/v1/rooms',
               close_callback: Optional[Callable[[str], None]] = None,
               *args,
               **kwargs):
    super().__init__(
        title='Server URL',
        modal=True,
        width_request=300,
        height_request=150,
        resizable=False,
        *args,
        **kwargs,
    )
    self.close_callback = close_callback
    self.url = ''

    box = Gtk.Box(
        orientation=Gtk.Orientation.VERTICAL,
        halign=Gtk.Align.CENTER,
        valign=Gtk.Align.CENTER,
        spacing=10,
    )
    self.set_child(box)

    entry = Gtk.Entry(
        placeholder_text='Enter the URL of the server',
        width_request=200,
        text=placeholder,
    )
    box.append(entry)

    def set_url():
      url = entry.get_text()
      if url:
        self.url = url
        self.close()

    ok_button = Gtk.Button(label='OK')
    ok_button.connect('clicked', lambda _: set_url())
    box.append(ok_button)
    self.present()
    tweak_titlebar(self)

  def do_close_request(self):
    if self.close_callback:
      self.close_callback(self.url)
    return self.close()
