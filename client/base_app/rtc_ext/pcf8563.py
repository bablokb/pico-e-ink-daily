#-----------------------------------------------------------------------------
# External RTC-support with PCF8563.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import rtc
from rtc_ext.ext_base import ExtBase
from adafruit_pcf8563.pcf8563 import PCF8563 as PCF_RTC

# --- class ExtPCF8563   ----------------------------------------------------------

class ExtPCF8563(ExtBase):

  # --- constructor   --------------------------------------------------------

  def __init__(self,i2c,wifi=None,net_update=False):
    """ constructor """

    rtc = PCF_RTC(i2c)
    super().__init__(rtc,wifi,net_update)

  # --- init rtc   -----------------------------------------------------------

  def _init_rtc(self):
    """ init rtc """

    self._rtc_ext.alarm_status    = False
    self._rtc_ext.alarm_interrupt = False
    self._rtc_ext.clockout_enabled = False

  # --- check power-state   --------------------------------------------------

  def _lost_power(self):
    """ check for power-loss, must be plemented by subclass """
    return self._rtc_ext.lost_power

  # --- set alarm    ---------------------------------------------------------

  def set_alarm(self,alarm_time):
    """ set alarm. Must be implemented by subclass """

    self._rtc_ext.alarm  = (alarm_time,"monthly")
    self._rtc_ext.alarm_interrupt = True
