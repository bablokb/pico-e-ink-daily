# -------------------------------------------------------------------------
# Display Agenda of the current day on a 5.7" ACEP e-paper display.
#
# This program needs an additional configuration file settings.py
# with wifi-credentials and server information.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-daily
#
# -------------------------------------------------------------------------

# --- imports   -----------------------------------------------------------

import time
import atexit

def at_exit(app):
  if not app:
    # constructor for app failed
    import displayio
    displayio.release_displays()
  else:
    app.at_exit()

start = time.monotonic()
from settings import app_config
from base_app.ui_application import UIApplication
from agenda import Agenda                  # data-provider and ui-provider

if getattr(app_config,"debug",False):
  time.sleep(5)

app = None
atexit.register(at_exit,app)
agenda = Agenda()                                 
app = UIApplication(agenda,agenda,with_rtc=True)
print(f"startup: {time.monotonic()-start:f}s")
app.run_once()
