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
import socket
import adafruit_requests

class WifiImpl:
  """ request-implementation using sockets from CPython """

  def __init__(self):
    """ constructor """
    self._http = None

  def connect(self):
    self._http = adafruit_requests.Session(socket)

  def get_json(self,url):
    response = self._http.get(url)
    result = response.json()
    response.close()
    return result

  @property
  def radio(self):
    """ return ourselves as radio """
    return self

  @property
  def connected(self):
    """ emulate radio.connected """
    return self._http is not None

class PygameConfig(HWConfig):
  """ GENERIC_LINUX_PC specific configuration-class """

  def get_display(self):
    """ return display """
    return PyGameDisplay(width=600,height=448,
                         native_frames_per_second=1)

  def bat_level(self):
    """ return battery level """
    return 3.6

  def status_led(self,value):
    """ set status LED """
    pass

  def wifi(self):
    """ return wifi-interface """
    return WifiImpl()

  def shutdown(self):
    """ leave program """
    sys.exit(0)

config = PygameConfig()
