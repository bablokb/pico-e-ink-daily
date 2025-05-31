# ----------------------------------------------------------------------------
# GENERIC_LINUX_PC.py: HAL for simulation with PygameDisplay
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-daily
# ----------------------------------------------------------------------------

import sys
import time

import socket
import adafruit_requests

from .hal_base import HalBase

class WifiImpl:
  """ request-implementation using sockets from CPython """

  def __init__(self,debug=False):
    """ constructor """
    self.debug = debug
    self._http = None

  def connect(self):
    self._http = adafruit_requests.Session(socket)

  def get(self,url):
    return self._http.get(url)

  @property
  def radio(self):
    """ return ourselves as radio """
    return self

  @property
  def connected(self):
    """ emulate radio.connected """
    return self._http is not None

class HalPygame(HalBase):
  """ GENERIC_LINUX_PC specific HAL-class """

  def bat_level(self):
    """ return battery level """
    return 3.6

  def led(self,value,color=None):
    """ set status LED (not-supported)"""
    pass

  def wifi(self,debug=False):
    """ return wifi-interface """
    return WifiImpl(debug=debug)

  def shutdown(self):
    """ leave program (here: wait for quit) """
    if not self._display:
      sys.exit(0)
    else:
      self.deep_sleep()

  def sleep(self,duration):
    if not self._display:
      super.sleep(duration)
      return

    start = time.monotonic()
    while time.monotonic()-start < duration:
      if self._display.check_quit():
        sys.exit(0)

  def check_key(self,name):
    """ check if key is pressed (currently not supported) """
    return False

  def deep_sleep(self,alarms=[]):
    """ activate deep-sleep (not supported, fall back to idle) """

    if not self._display:
      super().deep_sleep(alarms)
      return

    while True:
      if self._display.check_quit():
        sys.exit(0)

impl = HalPygame()
