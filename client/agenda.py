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

palette = displayio.Palette(7)
palette[0] = 0xFFFFFF
palette[1] = 0x000000
palette[2] = 0x0000FF
palette[3] = 0x00FF00
palette[4] = 0xFF0000
palette[5] = 0xFFFF00
palette[6] = 0xFFA500

WHITE  = 0
BLACK  = 1
BLUE   = 2
GREEN  = 3
RED    = 4
YELLOW = 5
ORANGE = 6

# map color-names to (BG_COLOR,FG_COLOR)
colors = {
  "white":  (WHITE,BLACK),
  "black":  (BLACK,WHITE),
  "blue":   (BLUE,WHITE),
  "green":  (GREEN,BLACK),
  "red":    (RED,BLACK),
  "yellow": (YELLOW,BLACK),
  "orange": (ORANGE,BLACK)
  }

ui_settings = {
  "DAY_FONT":  "fonts/DejaVuSerif-Bold-60.bdf",
  "DATE_FONT": "fonts/DejaVuSans-BoldOblique-35.bdf",
  "TIME_FONT": "fonts/DejaVuSerif-BoldItalic-20.bdf",
  "TEXT_FONT": "fonts/DejaVuSerif-20.bdf",
  "STATUS_FONT": "fonts/DejaVuSerif-18.bdf",
  "MARGIN":    5,
  "PADDING":   3
  }

# --- Agenda Class for layout   ----------------------------------------------

class Agenda:

  # --- constructor   --------------------------------------------------------

  def __init__(self,display):
    """ constructor: create ressources """

    self._display     = display
    self._time_font   = bitmap_font.load_font(ui_settings["TIME_FONT"])
    self._text_font   = bitmap_font.load_font(ui_settings["TEXT_FONT"])
    self._status_font = bitmap_font.load_font(ui_settings["STATUS_FONT"])
    self._margin      = ui_settings["MARGIN"]
    self._padding     = ui_settings["PADDING"]

  # --- helper method for debugging   ----------------------------------------

  def print_size(self,label,obj):
    """ print size of object """
    print(f"{label} w,h: {obj.width},{obj.height}")

  # --- create box with day-number   -----------------------------------------

  def _get_day_box(self):
    """ create box with day-number """

    day_box = displayio.Group()

    if self._data["weekday"]:
      bg_color = BLACK
    else:
      bg_color = RED
    day_font = bitmap_font.load_font(ui_settings["DAY_FONT"])
    day = label.Label(day_font,text=self._data["day"],
                      color=palette[WHITE],
                      background_color=palette[bg_color],
                      background_tight=True,
                      anchor_point=(0,0),
                      anchored_position=(self._margin,self._margin))

    background = Rectangle(pixel_shader=palette,x=0,y=0,
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

    sep = Line(0,h,self._display.width,h,color=palette[BLACK])
    header.append(sep)

    date_font   = bitmap_font.load_font(ui_settings["DATE_FONT"])
    date = label.Label(date_font,text=self._data["date"],
                      color=palette[BLACK],
                      background_color=palette[WHITE],
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
                         color=palette[BLACK],
                         background_color=palette[WHITE],
                         base_alignment=True,
                         anchor_point=(0,1),
                         anchored_position=(self._margin,
                                            self._display.height-self._margin))
    color = palette[BLACK]
    if self._data['bat_level'] < 3.1:
      color = RED
    elif self._data['bat_level'] < 3.3:
      color = ORANGE

    level = label.Label(self._status_font,
                        text=f"{self._data['bat_level']:0.1f}V",
                        color=color,
                        background_color=palette[WHITE],
                        base_alignment=True,
                        anchor_point=(1,1),
                        anchored_position=(self._display.width-self._margin,
                                            self._display.height-self._margin))

    h = max(status.bounding_box[3],level.bounding_box[3]) + 2*self._margin
    status.anchor_point = (0,level.bounding_box[3]/status.bounding_box[3])
    sep = Line(0,self._display.height-h,
               self._display.width,self._display.height-h,
               color=palette[BLACK])

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
                       color=palette[BLACK],
                       background_color=palette[WHITE])
    ts = label.Label(self._time_font,
                       text="23:59",
                       background_tight=True,
                       color=palette[BLACK],
                       background_color=palette[WHITE])
    h_box      = 2*max(text.bounding_box[3],ts.bounding_box[3]) + 3*self._padding
    txt_offset = self._margin + ts.bounding_box[2] + self._margin

    # create all agenda-entries
    events = displayio.Group()
    y = 0
    for event in self._data["events"]:
      entry = displayio.Group()
      bg_color,color = colors[event["color"]]

      # create background for entry
      background = Rectangle(pixel_shader=palette,x=self._margin,y=y,
                             width=self._display.width - 2*self._margin,
                             height=h_box,
                             color_index=bg_color)
      entry.append(background)

      # create time-info (except for full-day events)
      if not (event["start"] == "00:00" and event["end"] == "23:59"):
        ts  = label.Label(self._time_font,
                          text=event["start"],
                          background_tight=True,
                          color=palette[color],
                          background_color=palette[bg_color],
                          anchor_point=(0,0.5),
                          anchored_position=(self._margin,y+int(0.3*h_box)))
        entry.append(ts)
        ts  = label.Label(self._time_font,
                          text=event["end"],
                          background_tight=True,
                          color=palette[color],
                          background_color=palette[bg_color],
                          anchor_point=(0,0.5),
                          anchored_position=(self._margin,y+int(0.75*h_box)))
        entry.append(ts)

      # create event-info
      text = label.Label(self._text_font,
                         text=event["summary"],
                         background_tight=True,
                         color=palette[color],
                         background_color=palette[bg_color],
                         anchor_point=(0,0.5),
                         anchored_position=(txt_offset,y+int(0.3*h_box)))
      entry.append(text)
      if event["location"]:
        text = label.Label(self._text_font,
                           text=event["location"],
                           background_tight=True,
                           color=palette[color],
                           background_color=palette[bg_color],
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
    background = Rectangle(pixel_shader=palette,x=0,y=0,
                           width=self._display.width,
                           height=self._display.height,
                           color_index=WHITE)
    g.append(background)

    (header,h) = self._get_header()
    g.append(header)
    gc.collect()

    events = self._get_events()
    events.y = h + self._margin
    g.append(events)

    g.append(self._get_footer())
    return g
