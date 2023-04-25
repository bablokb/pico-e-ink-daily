# -------------------------------------------------------------------------
# Generic class for e-ink based applications.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-daily
#
# -------------------------------------------------------------------------

# --- configuration constants   -------------------------------------------

WITH_TEST_DATA = False

# --- imports   -----------------------------------------------------------

import builtins
import time
start = time.monotonic()
import board

# import board-specific implementations
try:
  config_file = "config."+board.board_id.replace(".","_")
  hw_impl = builtins.__import__(config_file,None,None,["config"],0)
  print("using board-specific implementation")
except:
  raise
  config_file = "config.def_config"
  hw_impl = builtins.__import__(config_file,None,None,["config"],0)
  print("using default implementation")

from config.secrets import secrets
from agenda import Agenda

# --- application class   ----------------------------------------------------

class EInkApp:

  # --- constructor   --------------------------------------------------------

  def __init__(self,with_rtc=True):
    """ constructor """

    self._setup(with_rtc)  # setup hardware
    if with_rtc:
      self._update_rtc()   # update internal rtc from external rtc/internet

  # --- setup hardware   -----------------------------------------------------

  def _setup(self,with_rtc):
    """ setup hardware """
    
    self.display    = hw_impl.config.get_display()
    self._bat_level = hw_impl.config.bat_level
    self._wifi      = hw_impl.config.wifi()
    if with_rtc:
      self._rtc_ext   = hw_impl.config.get_rtc_ext()
    self._shutdown  = hw_impl.config.shutdown

  # --- update rtc   ---------------------------------------------------------

  def _update_rtc(self):
    """ update rtc """
    pass

  # --- update data from server   --------------------------------------------

  def update_data(self):
    """ update data """

    try:
      self._wifi.connect()
      self._data = self._wifi.get(secrets.url)
    except:
      if WITH_TEST_DATA:
        from testdata import values
        self._data = values
      else:
        self._data = {}
        self._data["bat_level"] = self._bat_level()
        raise
    self._data["bat_level"] = self._bat_level()

  # --- update display   -----------------------------------------------------

  def update_display(self,content):
    """ update display """

    self.display.show(content)
    if hasattr(self.display,"time_to_refresh"):
      time.sleep(self.display.time_to_refresh)   # will be >0 only during dev.
    self.display.refresh()
    if hasattr(self.display,"time_to_refresh"):
      time.sleep(self.display.time_to_refresh)

  # --- shutdown device   ----------------------------------------------------

  def shutdown(self):
    """ turn off device """
    self._shutdown()

  # --- main application loop   ----------------------------------------------

  def run(self):
    """ main application loop """

    # pygame test-environment
    if hasattr(self.display,"check_quit"):
      self.update_data()
      self.update_display()
      while True:
        if self.display.check_quit():
          self.shutdown()
        time.sleep(0.5)

    # running on real hardware
    else:
      start = time.monotonic()
      self.update_data()
      print(f"fetch_agenda: {time.monotonic()-start:f}s")
      self.update_display()
      print(f"update_display: {time.monotonic()-start:f}s")
      self.shutdown()
      time.sleep(60)
