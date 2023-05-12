# -------------------------------------------------------------------------
# Display Agenda of the current day on a 5.7" ACEP e-paper display.
#
# This class implements a standard frame (header and footer) for the content.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-daily
#
# -------------------------------------------------------------------------

import time
import gc
import displayio
from vectorio import Rectangle
from adafruit_display_text import label
from adafruit_display_shapes.line import Line
from adafruit_bitmap_font import bitmap_font

from ui_settings import UI_SETTINGS, COLORS, UI_COLOR_MAP, UI_PALETTE

# --- Frame Class for layout   ----------------------------------------------

class Frame:

  # --- constructor   --------------------------------------------------------

  def __init__(self,display,data):
    """ constructor: create ressources """

    self._display     = display
    self._data        = data
    self._status_font = bitmap_font.load_font(UI_SETTINGS.STATUS_FONT)
    self._margin      = UI_SETTINGS.MARGIN

  # --- create root-group   --------------------------------------------------

  def get_group(self):
    """ create root-group """

    g = displayio.Group()
    background = Rectangle(pixel_shader=UI_PALETTE,x=0,y=0,
                           width=self._display.width,
                           height=self._display.height,
                           color_index=UI_SETTINGS.BACKGROUND)
    g.append(background)
    return g

  # --- create box with day-number   -----------------------------------------

  def _get_day_box(self):
    """ create box with day-number """

    day_box = displayio.Group()

    if self._data["weekday"]:
      bg_color = COLORS.BLACK
    else:
      bg_color = COLORS.RED
    day_font = bitmap_font.load_font(UI_SETTINGS.DAY_FONT)
    day = label.Label(day_font,text=self._data["day"],
                      color=UI_PALETTE[UI_SETTINGS.BACKGROUND],
                      background_color=UI_PALETTE[bg_color],
                      background_tight=True,
                      anchor_point=(0,0),
                      anchored_position=(self._margin,self._margin))

    background = Rectangle(pixel_shader=UI_PALETTE,x=0,y=0,
                           width=day.bounding_box[2]+2*self._margin,
                           height=day.bounding_box[3]+2*self._margin,
                           color_index=bg_color)
    day_box.append(background)
    day_box.append(day)
    return (day_box,background.width,background.height)

  # --- create header   ------------------------------------------------------

  def get_header(self):
    """ create complete header """

    header = displayio.Group()
    
    day_box,w,h = self._get_day_box()
    day_box.x = self._display.width-w-self._margin
    day_box.y = 0
    header.append(day_box)

    sep = Line(0,h,self._display.width,h,color=UI_PALETTE[UI_SETTINGS.FOREGROUND])
    header.append(sep)

    date_font   = bitmap_font.load_font(UI_SETTINGS.DATE_FONT)
    date = label.Label(date_font,text=self._data["date"],
                      color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                      background_color=UI_PALETTE[UI_SETTINGS.BACKGROUND],
                      background_tight=True,
                      anchor_point=(0,1),
                       anchored_position=(self._margin,h-self._margin))
    header.append(date)
    return (header,h)

  # --- create footer   ------------------------------------------------------

  def get_footer(self):
    """ create complete footer """

    footer = displayio.Group()
    status = label.Label(self._status_font,
                         text=f"Updated: {self._data['now']}",
                         color=UI_PALETTE[UI_SETTINGS.FOREGROUND],
                         background_color=UI_PALETTE[UI_SETTINGS.BACKGROUND],
                         base_alignment=True,
                         anchor_point=(0,1),
                         anchored_position=(self._margin,
                                            self._display.height-self._margin))
    color = UI_PALETTE[UI_SETTINGS.FOREGROUND]
    if self._data['bat_level'] < 3.1:
      color = UI_PALETTE[COLORS.RED]
    elif self._data['bat_level'] < 3.3:
      color = UI_PALETTE[COLORS.ORANGE]

    level = label.Label(self._status_font,
                        text=f"{self._data['bat_level']:0.1f}V",
                        color=color,
                        background_color=UI_PALETTE[UI_SETTINGS.BACKGROUND],
                        base_alignment=True,
                        anchor_point=(1,1),
                        anchored_position=(self._display.width-self._margin,
                                            self._display.height-self._margin))

    h = max(status.bounding_box[3],level.bounding_box[3]) + 2*self._margin
    status.anchor_point = (0,level.bounding_box[3]/status.bounding_box[3])
    sep = Line(0,self._display.height-h,
               self._display.width,self._display.height-h,
               color=UI_PALETTE[UI_SETTINGS.FOREGROUND])

    footer.append(status)
    footer.append(level)
    footer.append(sep)
    return footer
