# Copyright (C) 2024 seb0xff
#
# This program is licensed under the GNU Affero General Public License.
# You should have received a copy of this license along with this program.
# If not, see <https://www.gnu.org/licenses/>.

import gi
from logger import logger

gi.require_version('Gdk', '4.0')

from gi.repository import Gtk, Gdk  # type: ignore


def tweak_titlebar(window: Gtk.Window):
  # ensure it's macos
  from sys import platform
  if platform != 'darwin':
    return

  try:
    gi.require_version('Gnt', '0.1')
    from gi.repository import Gnt  # type: ignore
    tweaker = Gnt.MacosWindow(window=window)
    color = Gdk.RGBA()
    color.parse('rgb(18,19,29)')
    tweaker.set_titlebar_color(color)

  except Exception as e:
    logger.info(f'Cannot tweak titlebar, falling back to defaults: {e}')
