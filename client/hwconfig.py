# ----------------------------------------------------------------------------
# HWConfig: Base-class with hardware-specific methods. Some methods are
# usually overridden by board-specific sub-classes.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-daily
#
# ----------------------------------------------------------------------------

import board
from digitalio import DigitalInOut, Direction

class HWConfig:
  def __init__(self):
    """ constructor """
    pass

  def status_led(self,value):
    """ set status LED """
    if not hasattr(self,"_led"):
      self._led = DigitalInOut(board.LED)
      self._led.direction = Direction.OUTPUT
    self._led.value = value

  def bat_level(self):
    """ return battery level """
    if hasattr(board,"VOLTAGE_MONITOR"):
      from analogio import AnalogIn
      adc = AnalogIn(board.VOLTAGE_MONITOR)
      level = adc.value *  3 * 3.3 / 65535
      adc.deinit()
      return level
    else:
      return 0.0

  def wifi(self):
    """ return wifi-interface """
    from wifi_impl_builtin import WifiImpl
    return WifiImpl()

  def get_display(self):
    """ return display """
    return board.DISPLAY

  def get_rtc_ext(self):
    """ return external rtc, if available """
    return None

  def shutdown(self):
    pass
