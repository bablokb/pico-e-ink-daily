# ----------------------------------------------------------------------------
# pimoroni_inky_frame_5_7.py: HW-config for Pimoroni InkyFrame 5.7
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-daily
#
# ----------------------------------------------------------------------------

import board

from hwconfig import HWConfig
from digitalio import DigitalInOut, Direction

class InkyFrame57Config(HWConfig):
  """ InkyFrame 5.7 specific configuration-class """

  def status_led(self,value):
    """ set status LED """
    if not hasattr(self,"_led"):
      self._led = DigitalInOut(board.LED_ACT)
      self._led.direction = Direction.OUTPUT
    self._led.value = value

  def get_rtc_ext(self):
    """ return external rtc, if available """
    from rtc_ext.pcf85063a import ExtPCF85063A
    i2c = board.I2C()
    return ExtPCF85063A(i2c)

  def shutdown(self):
    """ turn off power by pulling enable pin low """
    board.ENABLE_DIO.value = 0

config = InkyFrame57Config()
