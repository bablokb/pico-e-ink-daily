# ----------------------------------------------------------------------------
# GENERIC_LINUX_PC.py: HW-config for simulation with PygameDisplay
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-daily
#
# ----------------------------------------------------------------------------

import sys
import board
from blinka_displayio_pygamedisplay import PyGameDisplay
from hwconfig import HWConfig

class PygameConfig(HWConfig):
  """ GENERIC_LINUX_PC specific configuration-class """

  def get_display(self):
    """ return display """
    return PyGameDisplay(width=600,height=448,
                         native_frames_per_second=1)

  def bat_level(self):
    """ return battery level """
    return 3.6

  def shutdown(self):
    """ leave program """
    sys.exit(0)

config = PygameConfig()
