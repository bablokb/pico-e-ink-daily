# -------------------------------------------------------------------------
# Display Agenda of the current day on a 5.7" ACEP e-paper display.
#
# This file contains settings related to the UI.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-daily
#
# -------------------------------------------------------------------------

from displayio import Palette

class Settings:
  pass

UI_PALETTE = Palette(7)
UI_PALETTE[0] = 0xFFFFFF
UI_PALETTE[1] = 0x000000
UI_PALETTE[2] = 0x0000FF
UI_PALETTE[3] = 0x00FF00
UI_PALETTE[4] = 0xFF0000
UI_PALETTE[5] = 0xFFFF00
UI_PALETTE[6] = 0xFFA500

COLORS = Settings()
COLORS.WHITE  = 0
COLORS.BLACK  = 1
COLORS.BLUE   = 2
COLORS.GREEN  = 3
COLORS.RED    = 4
COLORS.YELLOW = 5
COLORS.ORANGE = 6

# map color-names to (BG_COLOR,FG_COLOR)
UI_COLOR_MAP = {
  "white":  (COLORS.WHITE,COLORS.BLACK),
  "black":  (COLORS.BLACK,COLORS.WHITE),
  "blue":   (COLORS.BLUE,COLORS.WHITE),
  "green":  (COLORS.GREEN,COLORS.WHITE),
  "red":    (COLORS.RED,COLORS.BLACK),
  "yellow": (COLORS.YELLOW,COLORS.BLACK),
  "orange": (COLORS.ORANGE,COLORS.BLACK)
  }

UI_SETTINGS = Settings()
UI_SETTINGS.DAY_FONT =  "fonts/DejaVuSerif-Bold-60.bdf"
UI_SETTINGS.DATE_FONT = "fonts/DejaVuSans-BoldOblique-35.bdf"
UI_SETTINGS.TIME_FONT = "fonts/DejaVuSerif-BoldItalic-20.bdf"
UI_SETTINGS.TEXT_FONT = "fonts/DejaVuSerif-20.bdf"
UI_SETTINGS.STATUS_FONT = "fonts/DejaVuSerif-18.bdf"
UI_SETTINGS.MARGIN =    5
UI_SETTINGS.PADDING =   3
UI_SETTINGS.FOREGROUND = COLORS.BLACK
UI_SETTINGS.BACKGROUND = COLORS.WHITE
UI_SETTINGS.NO_NETWORK = "images/no-server-connection.bmp"
UI_SETTINGS.NO_EVENTS  = "images/empty-agenda.bmp"
