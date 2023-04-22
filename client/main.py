# -------------------------------------------------------------------------
# Display Agenda of the current day on a 5.7" ACEP e-paper display.
#
# This program needs an additional configuration file secrets.py
# with wifi-credentials and server information.
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

class App:

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """

    self._setup()          # setup hardware
    self._update_rtc()     # update internal rtc from external rtc/internet

  # --- setup hardware   -----------------------------------------------------

  def _setup(self):
    """ setup hardware """
    
    self.display    = hw_impl.config.get_display()
    self._bat_level = hw_impl.config.bat_level
    self._wifi      = hw_impl.config.wifi()
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
        raise
    self._data["bat_level"] = self._bat_level()

  # --- update display   -----------------------------------------------------

  def update_display(self):
    """ update display """

    agenda = Agenda(self.display)
    self.display.show(agenda.get_content(self._data))
    self.display.refresh()
    if hasattr(self.display,"time_to_refresh"):
      time.sleep(self.display.time_to_refresh)

  # --- shutdown device   ----------------------------------------------------

  def shutdown(self):
    """ turn off device """
    self._shutdown()

# --- main loop   ------------------------------------------------------------

app = App()
print(f"startup: {time.monotonic()-start:f}s")

# pygame test-environment
if hasattr(app.display,"check_quit"):
  app.update_data()
  app.update_display()
  while True:
    if app.display.check_quit():
      app.shutdown()
    time.sleep(0.5)

# running on real hardware
else:
  while True:
    start = time.monotonic()
    app.update_data()
    print(f"fetch_agenda: {time.monotonic()-start:f}s")
    app.update_display()
    print(f"update_display: {time.monotonic()-start:f}s")
    app.shutdown()
    time.sleep(60)
