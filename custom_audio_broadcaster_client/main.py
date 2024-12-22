import sys
import asyncio
import threading
from os import path as p
import gi
from typing import Optional, Callable
from room_row import RoomRow
from response_preview import ResponsePreview
from gstreamer_pipeline import GstreamerPipeline
from client import Client, Room
from url_dialog import UrlDialog
from tweak_titlebar import tweak_titlebar
from play_box import PlayBox
from volume_box import VolumeBox
from logger import logger

gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('GLib', '2.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gdk, GLib  # type: ignore

PROJECT_DIR_ABS_PATH = p.abspath(p.realpath(p.dirname(__file__)))
CSS_STYLESHEET_ABS_PATH = p.join(PROJECT_DIR_ABS_PATH, 'styles.css')
REFRESH_ICON = 'view-refresh-symbolic'


class MainWindow(Gtk.ApplicationWindow):

  def __init__(self, url: str, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if not url:
      raise ValueError('URL cannot be empty')
    self.pipeline = GstreamerPipeline(
        # uri=f'file://{p.join(PROJECT_DIR_ABS_PATH, "test.mp3")}')
    )
    self.rooms: list[Room] = []
    self.current_room_idx = 0
    self.url = url
    self.client = Client(url=self.url)
    self.lock = asyncio.Lock()

    # Window
    self.set_default_size(450, 350)
    self.set_resizable(False)
    self.set_title('Broadcaster Client')

    split_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    self.set_child(split_box)

    # Rooms column
    rooms_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    split_box.append(rooms_column)

    # Rooms column header
    rooms_column_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    rooms_column_header.add_css_class('column-header')
    rooms_column.append(rooms_column_header)

    # Ask for URL button
    open_url_entry_dialog_button = Gtk.Button.new_from_icon_name(
        'emblem-system-symbolic')
    open_url_entry_dialog_button.set_css_classes(
        ['flat', 'circular', 'ask-url-btn'])

    # open_url_entry_dialog_button.connect(
    #     'clicked',
    #     lambda _: self.open_url_entry_dialog(lambda url: self.update_url(url)))
    open_url_entry_dialog_button.connect(
        'clicked', lambda _: UrlDialog(application=self.get_application(),
                                       close_callback=self.update_url))
    rooms_column_header.append(open_url_entry_dialog_button)

    # Refresh button
    refresh_button = Gtk.Button.new_from_icon_name(REFRESH_ICON)
    refresh_button.set_css_classes(['flat', 'circular', 'refresh-button'])
    refresh_button.connect('clicked', lambda _: self.refresh_rooms())
    rooms_column_header.append(refresh_button)

    # Room list
    self.scrolled_window = Gtk.ScrolledWindow(width_request=150, vexpand=True)
    self.room_list = Gtk.ListBox()
    self.room_list.connect("row-selected", self.on_row_selected)
    self.room_list.set_css_classes(['navigation-sidebar'])
    self.scrolled_window.set_child(self.room_list)
    rooms_column.append(self.scrolled_window)

    main_content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

    # Response preview
    self.preview = ResponsePreview('')
    self.preview.set_size_request(-1, 310)
    main_content_box.append(self.preview)

    # Audio controls
    audio_controls_box = Gtk.Box(
        orientation=Gtk.Orientation.HORIZONTAL,
        spacing=5,
        hexpand=True,
        height_request=40,
    )
    audio_controls_box.add_css_class('audio-controls')
    main_content_box.append(audio_controls_box)

    # Play box
    play_box = PlayBox(self.pipeline)
    audio_controls_box.append(play_box)

    # Volume box
    volume_box = VolumeBox(pipeline=self.pipeline)
    audio_controls_box.append(volume_box)

    split_box.append(main_content_box)
    self.updater_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(self.updater_loop)
    self.updater_thread = threading.Thread(
        target=self.updater_loop.run_forever, args=(), daemon=True)
    self.updater_thread.start()
    self.refresh_rooms()
    self.refresh_room_data(one_shot=False)

    self.present()
    tweak_titlebar(self)

  def on_row_selected(self, listbox, row):
    if row:
      self.current_room_idx = row.get_index()
      logger.info(f"Row {self.current_room_idx} is selected")
      self.pipeline.set_uri(self.rooms[self.current_room_idx].audioUrls.srt)
      self.refresh_room_data()

  def update_url(self, url: str):
    if not url:
      return
    self.url = url
    self.client.url = url
    self.refresh_rooms()
    self.refresh_room_data()

  async def update_rooms(self):

    def update(prev_sel_room: Optional[str] = None):
      self.room_list.remove_all()
      for room in self.rooms:
        row = RoomRow(
            title=room.title,
            subtitle=room.path,
            description=room.description,
        )
        self.room_list.append(row)

      self.current_room_idx = 0
      if prev_sel_room:
        for i, room in enumerate(self.rooms):
          if room.path == prev_sel_room.path:
            self.current_room_idx = i
            break

      self.room_list.select_row(
          self.room_list.get_row_at_index(self.current_room_idx))

    try:
      async with self.lock:
        prev_sel_room = self.rooms[
            self.current_room_idx] if self.current_room_idx < len(
                self.rooms) else None
        self.rooms = await self.client.fetch_rooms()
        GLib.idle_add(lambda: update(prev_sel_room))
    except Exception as e:
      logger.error(f'Cannot update rooms: {e}')

  async def update_room_data(self, one_shot=False):

    def update(room_data):
      self.preview.set_str(room_data)

    while True:
      try:
        async with self.lock:
          if self.current_room_idx < len(self.rooms):
            room_data = await self.client.fetch_room_data(
                self.rooms[self.current_room_idx])
            GLib.idle_add(lambda: update(room_data))
      except Exception as e:
        logger.error(f'Cannot update current room\'s data: {e}')
      if one_shot:
        break
      await asyncio.sleep(3)

  def refresh_rooms(self):
    asyncio.run_coroutine_threadsafe(self.update_rooms(), self.updater_loop)

  def refresh_room_data(self, one_shot=True):
    asyncio.run_coroutine_threadsafe(self.update_room_data(one_shot=one_shot),
                                     self.updater_loop)


class MyApp(Adw.Application):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

    # CSS
    css_provider = Gtk.CssProvider()
    css_provider.load_from_path(CSS_STYLESHEET_ABS_PATH)
    display = Gdk.Display.get_default()
    Gtk.StyleContext.add_provider_for_display(
        display, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

  def open_main_window(self, url: str):
    logger.info(f'Opening main window with URL: {url}')
    if not url:
      return
    MainWindow(application=self, url=url)

  def do_activate(self):
    UrlDialog(application=self, close_callback=self.open_main_window)


if __name__ == '__main__':
  app = MyApp(application_id='Custom.Audio.Broadcaster.Client')
  app.run(sys.argv)
