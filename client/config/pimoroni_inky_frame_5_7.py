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

  def get_rtc_ext(self,net_update=False):
    """ return external rtc, if available """
    from rtc_ext.ext_base import ExtBase
    i2c = board.I2C()
    return ExtBase.create("PCF85063",i2c,net_update=net_update)

  def shutdown(self):
    """ turn off power by pulling enable pin low """
    self._wait_for_display()
    board.ENABLE_DIO.value = 0

  def _wait_for_display(self):
    """ wait for display update to finish """

    # we check the busy-pin of the shift-register
    import keypad, time
    shift_reg = keypad.ShiftRegisterKeys(
      clock = board.SWITCH_CLK,
      data  = board.SWITCH_OUT,
      latch = board.SWITCH_LATCH,
      key_count = 8,
      value_to_latch = True,
      value_when_pressed = True
    )

    queue = shift_reg.events
    while True:
      if not len(queue):
        time.sleep(0.1)
        continue
      ev = queue.get()
      if ev.key_number == board.KEYCODES.INKY_BUS and ev.pressed:
        # i.e. busy-pin is high, so no longer busy
        shift_reg.deinit()
        return

config = InkyFrame57Config()
