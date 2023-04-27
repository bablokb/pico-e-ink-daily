# -------------------------------------------------------------------------
# Display Agenda of the current day on a 5.7" ACEP e-paper display.
#
# This class implements the actual layout of all items on the display.
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

# --- Agenda Class for layout   ----------------------------------------------

class Agenda:

  # --- constructor   --------------------------------------------------------

  def __init__(self,display):
    """ constructor: create ressources """

    self._display     = display
    self._time_font   = bitmap_font.load_font(UI_SETTINGS.TIME_FONT)
    self._text_font   = bitmap_font.load_font(UI_SETTINGS.TEXT_FONT)
    self._status_font = bitmap_font.load_font(UI_SETTINGS.STATUS_FONT)
    self._margin      = UI_SETTINGS.MARGIN
    self._padding     = UI_SETTINGS.PADDING

  # --- helper method for debugging   ----------------------------------------

  def print_size(self,label,obj):
    """ print size of object """
    print(f"{label} w,h: {obj.width},{obj.height}")

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
                      color=UI_PALETTE[COLORS.WHITE],
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

  def _get_header(self):
    """ create complete header """

    header = displayio.Group()
    
    day_box,w,h = self._get_day_box()
    day_box.x = self._display.width-w
    day_box.y = 0
    header.append(day_box)

    sep = Line(0,h,self._display.width,h,color=UI_PALETTE[COLORS.BLACK])
    header.append(sep)

    date_font   = bitmap_font.load_font(UI_SETTINGS.DATE_FONT)
    date = label.Label(date_font,text=self._data["date"],
                      color=UI_PALETTE[COLORS.BLACK],
                      background_color=UI_PALETTE[COLORS.WHITE],
                      background_tight=True,
                      anchor_point=(0,1),
                       anchored_position=(self._margin,h-self._margin))
    header.append(date)
    return (header,h)

  # --- create footer   ------------------------------------------------------

  def _get_footer(self):
    """ create complete footer """

    footer = displayio.Group()
    status = label.Label(self._status_font,
                         text=f"Updated: {self._data['now']}",
                         color=UI_PALETTE[COLORS.BLACK],
                         background_color=UI_PALETTE[COLORS.WHITE],
                         base_alignment=True,
                         anchor_point=(0,1),
                         anchored_position=(self._margin,
                                            self._display.height-self._margin))
    color = UI_PALETTE[COLORS.BLACK]
    if self._data['bat_level'] < 3.1:
      color = COLORS.RED
    elif self._data['bat_level'] < 3.3:
      color = COLORS.ORANGE

    level = label.Label(self._status_font,
                        text=f"{self._data['bat_level']:0.1f}V",
                        color=color,
                        background_color=UI_PALETTE[COLORS.WHITE],
                        base_alignment=True,
                        anchor_point=(1,1),
                        anchored_position=(self._display.width-self._margin,
                                            self._display.height-self._margin))

    h = max(status.bounding_box[3],level.bounding_box[3]) + 2*self._margin
    status.anchor_point = (0,level.bounding_box[3]/status.bounding_box[3])
    sep = Line(0,self._display.height-h,
               self._display.width,self._display.height-h,
               color=UI_PALETTE[COLORS.BLACK])

    footer.append(status)
    footer.append(level)
    footer.append(sep)
    return footer

  # --- create agenda events   -----------------------------------------------

  def _get_events(self):
    """ create agenda events """

    # each event-box has (up to) four labels. We first measure the maximum
    # sizes needed, then we create the events
    text = label.Label(self._text_font,
                       text="Mg",
                       background_tight=True,
                       color=UI_PALETTE[COLORS.BLACK],
                       background_color=UI_PALETTE[COLORS.WHITE])
    ts = label.Label(self._time_font,
                       text="23:59",
                       background_tight=True,
                       color=UI_PALETTE[COLORS.BLACK],
                       background_color=UI_PALETTE[COLORS.WHITE])
    h_box      = 2*max(text.bounding_box[3],ts.bounding_box[3]) + 3*self._padding
    txt_offset = self._margin + ts.bounding_box[2] + self._margin

    # create all agenda-entries
    events = displayio.Group()
    y = 0
    for event in self._data["events"]:
      entry = displayio.Group()
      bg_color,color = UI_COLOR_MAP[event["color"]]

      # create background for entry
      background = Rectangle(pixel_shader=UI_PALETTE,x=self._margin,y=y,
                             width=self._display.width - 2*self._margin,
                             height=h_box,
                             color_index=bg_color)
      entry.append(background)

      # create time-info (except for full-day events)
      if not (event["start"] == "00:00" and event["end"] == "23:59"):
        ts  = label.Label(self._time_font,
                          text=event["start"],
                          background_tight=True,
                          color=UI_PALETTE[color],
                          background_color=UI_PALETTE[bg_color],
                          anchor_point=(0,0.5),
                          anchored_position=(self._margin,y+int(0.3*h_box)))
        entry.append(ts)
        ts  = label.Label(self._time_font,
                          text=event["end"],
                          background_tight=True,
                          color=UI_PALETTE[color],
                          background_color=UI_PALETTE[bg_color],
                          anchor_point=(0,0.5),
                          anchored_position=(self._margin,y+int(0.75*h_box)))
        entry.append(ts)

      # create event-info
      text = label.Label(self._text_font,
                         text=event["summary"],
                         background_tight=True,
                         color=UI_PALETTE[color],
                         background_color=UI_PALETTE[bg_color],
                         anchor_point=(0,0.5),
                         anchored_position=(txt_offset,y+int(0.3*h_box)))
      entry.append(text)
      if event["location"]:
        text = label.Label(self._text_font,
                           text=event["location"],
                           background_tight=True,
                           color=UI_PALETTE[color],
                           background_color=UI_PALETTE[bg_color],
                           anchor_point=(0,0.5),
                           anchored_position=(txt_offset,y+int(0.75*h_box)))
        entry.append(text)

      # save entry and advance y-offset
      events.append(entry)
      gc.collect()
      y += h_box + self._padding

    return events

  # --- create complete content   --------------------------------------------

  def get_content(self,data):
    """ create content """

    self._data = data
    gc.collect()
    g = displayio.Group()
    background = Rectangle(pixel_shader=UI_PALETTE,x=0,y=0,
                           width=self._display.width,
                           height=self._display.height,
                           color_index=COLORS.WHITE)
    g.append(background)

    (header,h) = self._get_header()
    g.append(header)
    gc.collect()

    events = self._get_events()
    events.y = h + self._margin
    g.append(events)

    g.append(self._get_footer())
    return g
