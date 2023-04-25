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

from einkapp import EInkApp
from config.secrets import secrets
from agenda import Agenda

# --- application class   ----------------------------------------------------

class App(EInkApp):

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor """
    super().__init__(with_rtc=False)

  # --- update data from server   --------------------------------------------

  def update_data(self):
    """ update data """

    try:
      super().update_data()
    except:
      # TODO: implement error-display
      pass

  # --- update display   -----------------------------------------------------

  def update_display(self):
    """ update display """

    agenda = Agenda(self.display)
    super().update_display(agenda.get_content(self._data))

  # --- shutdown device   ----------------------------------------------------

  def shutdown(self):
    """ turn off device """
    self._shutdown()

# --- main loop   ------------------------------------------------------------

app = App()
print(f"startup: {time.monotonic()-start:f}s")
app.run()
