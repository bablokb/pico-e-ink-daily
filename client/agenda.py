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
from adafruit_display_text import label
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.line import Line
from adafruit_bitmap_font import bitmap_font

WHITE  = 0xFFFFFF
BLACK  = 0x000000
BLUE   = 0x0000FF
GREEN  = 0x00FF00
RED    = 0xFF0000
YELLOW = 0xFFFF00
ORANGE = 0xFFA500

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

values = {
  "day": "13",
  "date": "Donnerstag 13.04.2023",
  "now": "13.04.23 12:34",
  "weekday": True,
  "bat_level": 3.0,
  "events": [
     {
       "start": "00:00",
       "end": "23:59",
       "summary": "Naturfototage",
       "location": "",
       "color": "green"
     },
     {
       "start": "08:00",
       "end": "09:00",
       "summary": "Frühstück",
       "location": "Küche",
       "color": "green"
     },
     {
       "start": "09:00",
       "end": "10:00",
       "summary": "Migrations-Check",
       "location": "Meetingraum",
       "color": "orange"
     },
     {
       "start": "10:00",
       "end": "11:00",
       "summary": "Go-Live",
       "location": "",
       "color": "orange"
     },
     {
       "start": "14:00",
       "end": "16:00",
       "summary": "Meeting",
       "location": "Büro",
       "color": "blue"
     },
     {
       "start": "14:00",
       "end": "15:00",
       "summary": "Meeting2",
       "location": "Büro",
       "color": "red"
     },
     {
       "start": "15:00",
       "end": "16:00",
       "summary": "Meeting3",
       "location": "Büro",
       "color": "yellow"
     }
   ]
  }

ui_settings = {
  "DAY_FONT":  "fonts/DejaVuSerif-Bold-60.bdf",
  "DATE_FONT": "fonts/DejaVuSans-BoldOblique-35.bdf",
  "TIME_FONT": "fonts/DejaVuSerif-BoldItalic-20.bdf",
  "TEXT_FONT": "fonts/DejaVuSans-18.bdf",
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

    if values["weekday"]:
      bg_color = BLACK
    else:
      bg_color = RED
    day_font = bitmap_font.load_font(ui_settings["DAY_FONT"])
    day = label.Label(day_font,text=values["day"],
                      color=WHITE,
                      background_color=bg_color,
                      background_tight=True,
                      anchor_point=(0,0),
                      anchored_position=(self._margin,self._margin))
    
    background = Rect(x=0,y=0,
                      width=day.bounding_box[2]+2*self._margin,
                      height=day.bounding_box[3]+2*self._margin,
                fill=bg_color,outline=None,stroke=0)
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

    sep = Line(0,h,self._display.width,h,color=BLACK)
    header.append(sep)

    date_font   = bitmap_font.load_font(ui_settings["DATE_FONT"])
    date = label.Label(date_font,text=values["date"],
                      color=BLACK,
                      background_color=WHITE,
                      background_tight=True,
                      anchor_point=(0,1),
                       anchored_position=(self._margin,h-self._margin))
    header.append(date)
    return (header,h)

  # --- create footer   ------------------------------------------------------

  def _get_footer(self):
    """ create complete footer """

    footer = displayio.Group()
    status = label.Label(self._text_font,
                         text=f"Updated: {values['now']}",
                         color=BLACK,
                         background_color=WHITE,
                         base_alignment=True,
                         anchor_point=(0,1),
                         anchored_position=(self._margin,
                                            self._display.height-self._margin))
    color = BLACK
    if values['bat_level'] < 3.1:
      color = RED
    elif values['bat_level'] < 3.3:
      color = ORANGE

    level = label.Label(self._text_font,
                        text=f"{values['bat_level']:0.1f}V",
                        color=color,
                        background_color=WHITE,
                        base_alignment=True,
                        anchor_point=(1,1),
                        anchored_position=(self._display.width-self._margin,
                                            self._display.height-self._margin))

    h = max(status.bounding_box[3],level.bounding_box[3]) + 2*self._margin
    status.anchor_point = (0,level.bounding_box[3]/status.bounding_box[3])
    sep = Line(0,self._display.height-h,
               self._display.width,self._display.height-h,
               color=BLACK)

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
                       color=BLACK,
                       background_color=WHITE)
    ts = label.Label(self._time_font,
                       text="23:59",
                       background_tight=True,
                       color=BLACK,
                       background_color=WHITE)
    h_box      = 2*max(text.bounding_box[3],ts.bounding_box[3]) + 3*self._padding
    txt_offset = self._margin + ts.bounding_box[2] + self._margin

    # create all agenda-entries
    events = displayio.Group()
    y = 0
    for event in values["events"]:
      entry = displayio.Group()
      bg_color,color = colors[event["color"]]

      # create background for entry
      background = Rect(x=self._margin,y=y,
                        width=self._display.width - 2*self._margin,
                        height=h_box,
                        fill=bg_color,outline=None,stroke=0)
      entry.append(background)

      # create time-info (except for full-day events)
      if not (event["start"] == "00:00" and event["end"] == "23:59"):
        ts  = label.Label(self._time_font,
                          text=event["start"],
                          background_tight=True,
                          color=color,
                          background_color=bg_color,
                          anchor_point=(0,0.5),
                          anchored_position=(self._margin,y+int(0.3*h_box)))
        entry.append(ts)
        ts  = label.Label(self._time_font,
                          text=event["end"],
                          background_tight=True,
                          color=color,
                          background_color=bg_color,
                          anchor_point=(0,0.5),
                          anchored_position=(self._margin,y+int(0.75*h_box)))
        entry.append(ts)

      # create event-info
      text = label.Label(self._text_font,
                         text=event["summary"],
                         background_tight=True,
                         color=color,
                         background_color=bg_color,
                         anchor_point=(0,0.5),
                         anchored_position=(txt_offset,y+int(0.3*h_box)))
      entry.append(text)
      if event["location"]:
        text = label.Label(self._text_font,
                           text=event["location"],
                           background_tight=True,
                           color=color,
                           background_color=bg_color,
                           anchor_point=(0,0.5),
                           anchored_position=(txt_offset,y+int(0.75*h_box)))
        entry.append(text)

      # save entry and advance y-offset
      events.append(entry)
      gc.collect()
      y += h_box + self._padding

    return events

  # --- create complete content   --------------------------------------------

  def get_content(self):
    """ create content """

    gc.collect()
    g = displayio.Group()
    background = Rect(x=0,y=0,
                      width=self._display.width,
                      height=self._display.height,
                      fill=WHITE,outline=None,stroke=0)
    g.append(background)

    (header,h) = self._get_header()
    g.append(header)
    gc.collect()

    events = self._get_events()
    events.y = h + self._margin
    g.append(events)

    g.append(self._get_footer())
    return g
