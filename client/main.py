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
start = time.monotonic()
import supervisor
from einkapp import EInkApp
from agenda import Agenda                         # content-provider

app = EInkApp(Agenda(),with_rtc=True)
print(f"startup: {time.monotonic()-start:f}s")
app.run()
