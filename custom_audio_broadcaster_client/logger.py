# Copyright (C) 2024 seb0xff
#
# This program is licensed under the GNU Affero General Public License.
# You should have received a copy of this license along with this program.
# If not, see <https://www.gnu.org/licenses/>.

import logging

logger = logging.getLogger(__name__)

shell_handler = logging.StreamHandler()

logger.setLevel(logging.ERROR)

fmt_shell = '{levelname:<9} {filename}:{funcName}:{lineno} {message}'
date_fmt = '%Y/%m/%d %H:%M:%S'

shell_formatter = logging.Formatter(fmt_shell, date_fmt, style='{')

shell_handler.setFormatter(shell_formatter)

logger.addHandler(shell_handler)
