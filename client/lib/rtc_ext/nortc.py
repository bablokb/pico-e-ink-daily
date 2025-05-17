#-----------------------------------------------------------------------------
# Expose internal RTC as external RTC. This allows to maintain a uniform
# interface (especially the net-update feature will work with no physical
# RTC present).
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import rtc
from time import struct_time
from rtc_ext.ext_base import ExtBase

# --- class NoRTC   ----------------------------------------------------------

class NoRTC(ExtBase):

  # --- constructor   --------------------------------------------------------

  def __init__(self,i2c,wifi=None,net_update=False):
    """ constructor """

    self._unset = True
    super().__init__(rtc.RTC(),wifi,net_update)

  # --- check power-state   --------------------------------------------------

  def _lost_power(self):
    """ check for power-loss: assume power-loss if not set """
    return self._unset

  # --- facade for datetime   ------------------------------------------------

  @property
  def datetime(self) -> struct_time:
    return self._rtc_int.datetime

  @datetime.setter
  def datetime(self, value: struct_time):
    self._rtc_int.datetime = value
    self._unset = False
