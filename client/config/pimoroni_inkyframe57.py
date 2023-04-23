# ----------------------------------------------------------------------------
# pimoroni_inkyframe_5_7.py: HW-config for Pimoroni InkyFrame 5.7
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-daily
#
# ----------------------------------------------------------------------------

import board

from hwconfig import HWConfig

class InkyFrame57Config(HWConfig):
  """ InkyFrame 5.7 specific configuration-class """

  def get_rtc_ext(self):
    """ return external rtc, if available """
    from pcf85063a import PCF85063A
    i2c = board.I2C()
    return PCF85063A(i2c)

  def shutdown(self):
    """ turn off power by pulling enable pin low """
    board.ENABLE_DIO.value = 0

config = InkyFrame57Config()
