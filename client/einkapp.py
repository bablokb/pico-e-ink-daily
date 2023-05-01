# -------------------------------------------------------------------------
# Generic class for e-ink based applications.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-daily
#
# -------------------------------------------------------------------------

# --- imports   -----------------------------------------------------------

import builtins
import time
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

# --- application class   ----------------------------------------------------

class EInkApp:

  # --- constructor   --------------------------------------------------------

  def __init__(self,contentprovider,errorhandler,with_rtc=True):
    """ constructor """

    self._setup(with_rtc)  # setup hardware
    if with_rtc:
      self._update_rtc()   # update internal rtc from external rtc/internet

    self._cprovider = contentprovider
    self._ehandler  = errorhandler
    self._cprovider.set_display(self._display)
    self._ehandler.set_display(self._display)

  # --- setup hardware   -----------------------------------------------------

  def _setup(self,with_rtc):
    """ setup hardware """
    
    self._display   = hw_impl.config.get_display()
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

    start = time.monotonic()
    self._data = {}
    self._data["bat_level"] = self._bat_level()
    try:
      self._wifi.connect()
      self._data.update(self._wifi.get(secrets.url))
      print(f"update_data (ok): {time.monotonic()-start:f}s")
    except Exception as ex:
      self._ehandler.on_exception(ex)
      print(f"update_data (exception): {time.monotonic()-start:f}s")
      raise

  # --- update display   -----------------------------------------------------

  def update_display(self,content):
    """ update display """

    start = time.monotonic()
    self._display.show(content)
    print(f"update_display (show): {time.monotonic()-start:f}s")
    start = time.monotonic()
    if hasattr(self._display,"time_to_refresh"):
      time.sleep(self._display.time_to_refresh)   # will be >0 only during dev.
    self._display.refresh()
    if hasattr(self._display,"time_to_refresh"):
      time.sleep(self._display.time_to_refresh)
    print(f"update_display (refreshed): {time.monotonic()-start:f}s")

  # --- shutdown device   ----------------------------------------------------

  def shutdown(self):
    """ turn off device """
    self._shutdown()

  # --- main application loop   ----------------------------------------------

  def run(self):
    """ main application loop """

    # pygame test-environment
    if hasattr(self._display,"check_quit"):
      try:
        self.update_data()
        self.update_display(self._cprovider.get_content(self._data))
      except:
        self.update_display(self._ehandler.get_content())
      while True:
        if self._display.check_quit():
          self.shutdown()
        time.sleep(0.5)

    # running on real hardware
    else:
      try:
        self.update_data()
        self.update_display(self._cprovider.get_content(self._data))
      except:
        self.update_display(self._ehandler.get_content())
      self.shutdown()
      time.sleep(60)
