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

# --- imports   -----------------------------------------------------------

import time
start = time.monotonic()

from einkapp import EInkApp
from agenda import Agenda                         # content-provider
from errorhandler import ErrorHandler

app = EInkApp(Agenda(),ErrorHandler(),with_rtc=False)
app.blink(0.5)
print(f"startup: {time.monotonic()-start:f}s")
app.run()
