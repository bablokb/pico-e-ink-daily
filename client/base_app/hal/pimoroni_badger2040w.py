# ----------------------------------------------------------------------------
# pimoroni_badger2040w.py: HAL for Pimoroni Badger2040W
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
# ----------------------------------------------------------------------------

import board

from digitalio import DigitalInOut, Direction

from .hal_base import HalBase

class HalBadger2040W(HalBase):
  """ Badger2040W specific HAL-class """

  def _init_led(self,value):
    """ initialize LED/Neopixel """
    if not hasattr(self,"_led"):
      self._led = DigitalInOut(board.USER_LED)
      self._led.direction = Direction.OUTPUT

  def get_rtc_ext(self,net_update=False,debug=False):
    """ return external rtc, if available """
    from ..rtc_ext.ext_base import ExtBase
    i2c = board.I2C()
    return ExtBase.create("PCF85063",i2c,net_update=net_update,debug=debug)

  def shutdown(self):
    """ turn off power by pulling enable pin low """
    board.ENABLE_DIO.value = 0

    if not self._keypad:
      import keypad
      self._keypad = keypad.Keys(
        [board.SW_A, board.SW_B, board.SW_C, board.SW_UP, board.SW_DOWN],
        value_when_pressed=True,pull=True,
        interval=0.1,max_events=4
      )
    return self._keypad

impl = HalBadger2040W()
