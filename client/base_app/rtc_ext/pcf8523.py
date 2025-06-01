#-----------------------------------------------------------------------------
# External RTC-support with PCF8523.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import rtc
from rtc_ext.ext_base import ExtBase
from adafruit_pcf8523.pcf8523 import PCF8523 as PCF_RTC
from adafruit_pcf8523.clock   import Clock

# --- class ExtPCF8523   ----------------------------------------------------------

class ExtPCF8523(ExtBase):

  # --- constructor   --------------------------------------------------------

  def __init__(self,i2c,wifi=None,net_update=False):
    """ constructor """

    rtc = PCF_RTC(i2c)
    self._clock = Clock(rtc.i2c_device)
    super().__init__(rtc,wifi,net_update)

  # --- init rtc   -----------------------------------------------------------

  def _init_rtc(self):
    """ init rtc """

    self._rtc_ext.alarm_status    = False
    self._rtc_ext.alarm_interrupt = False
    self._clock.clockout_frequency = Clock.CLOCKOUT_FREQ_DISABLED

  # --- check power-state   --------------------------------------------------

  def _lost_power(self):
    """ check for power-loss, must be plemented by subclass """
    return self._rtc_ext.lost_power

  # --- set alarm    ---------------------------------------------------------

  def set_alarm(self,alarm_time):
    """ set alarm. Must be implemented by subclass """

    self._rtc_ext.alarm  = (alarm_time,"monthly")
    self._rtc_ext.alarm_interrupt = True
