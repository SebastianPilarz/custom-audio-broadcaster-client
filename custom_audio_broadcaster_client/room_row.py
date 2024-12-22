# Copyright (C) 2024 seb0xff
#
# This program is licensed under the GNU Affero General Public License.
# You should have received a copy of this license along with this program.
# If not, see <https://www.gnu.org/licenses/>.

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('GLib', '2.0')
from gi.repository import Gtk, Adw, GLib  # type: ignore


class RoomRow(Adw.ActionRow):

  def __init__(self, title: str, subtitle: str, description: str):
    title = title.replace('&', '&amp;')
    subtitle = subtitle.replace('&', '&amp;')
    description = description.replace('&', '&amp;')
    super().__init__(title=title, subtitle=f'<i>{subtitle}</i>')

    self.timer_id: int | None

    header_box = self.get_child()
    title_box = header_box.get_last_child().get_prev_sibling()
    assert isinstance(title_box,
                      Gtk.Box), "title_box must be an instance of Gtk.Box"
    title_box.set_valign(Gtk.Align.START)
    title_box.set_margin_top(6)

    desc_label = Gtk.Label(
        label=description,
        css_classes=['subtitle'],
        name='description',
        halign=Gtk.Align.START,
        lines=0,
        use_markup=True,
        wrap=True,
        margin_top=6,
        margin_bottom=4,
    )

    self.revealer = Gtk.Revealer(
        transition_type=Gtk.RevealerTransitionType.SLIDE_DOWN,
        transition_duration=500,
        child=desc_label,
        reveal_child=False,
        css_classes=['hidden'],
    )

    motionController = Gtk.EventControllerMotion()
    motionController.connect('enter', self.on_enter)
    motionController.connect('leave', self.on_leave)
    self.add_controller(motionController)

    title_box.append(self.revealer)

  def on_enter(self, controller, x, y):
    self.timer_id = GLib.timeout_add(500, self.on_enter_timeout)

  def on_leave(self, controller):
    if self.timer_id:
      GLib.source_remove(self.timer_id)
    self.revealer.set_css_classes(['hidden'])
    GLib.timeout_add(250, self.on_leave_timeout)

  def on_enter_timeout(self):
    self.revealer.set_reveal_child(True)
    self.revealer.set_css_classes(['visible'])
    self.timer_id = None
    return False

  def on_leave_timeout(self):
    self.revealer.set_reveal_child(False)
    return False
