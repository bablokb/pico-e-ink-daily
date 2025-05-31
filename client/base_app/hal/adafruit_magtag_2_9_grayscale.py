# ----------------------------------------------------------------------------
# adafruit_magtag_2_9_grayscale.py: board-specific setup for Magtag
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
#
# ----------------------------------------------------------------------------

import board
from analogio import AnalogIn
from digitalio import DigitalInOut, Direction

import neopixel

from .hal_base import HalBase

class HalMagtag(HalBase):
  """ Magtag specific HAL-class """

  def bat_level(self):
    """ return battery level """
    from analogio import AnalogIn
    adc = AnalogIn(board.BATTERY)
    level = (adc.value / 65535.0) * 3.3 * 2
    adc.deinit()
    return level

  def get_keypad(self):
    """ return configured keypad """

    if not self._keypad:
      import keypad
      self._keypad = keypad.Keys(
        [board.D14,board.D12,board.D15,board.D11],
        value_when_pressed=False,pull=True,
        interval=0.1,max_events=4
      )
    return self._keypad

impl = HalMagtag()
