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
import traceback

from vectorio import Rectangle
from adafruit_display_text import label
from adafruit_display_shapes.line import Line
from adafruit_bitmap_font import bitmap_font

from ui_settings import UI_SETTINGS, COLORS, UI_COLOR_MAP, UI_PALETTE
from frame import Frame

# --- Agenda Class for layout   ----------------------------------------------

class Agenda:

  # --- constructor   --------------------------------------------------------

  def __init__(self):
    """ constructor: create ressources """

    self._time_font   = bitmap_font.load_font(UI_SETTINGS.TIME_FONT)
    self._text_font   = bitmap_font.load_font(UI_SETTINGS.TEXT_FONT)
    self._margin      = UI_SETTINGS.MARGIN
    self._padding     = UI_SETTINGS.PADDING
    self.app          = None

  # --- helper method for debugging   ----------------------------------------

  def print_size(self,label,obj):
    """ print size of object """
    print(f"{label} w,h: {obj.width},{obj.height}")

  # --- create box with day-number   -----------------------------------------

  def _get_day_box(self):
    """ create box with day-number """

    day_box = displayio.Group()

    if self.app.data["weekday"]:
      bg_color = COLORS.BLACK
    else:
      bg_color = COLORS.RED
    day_font = bitmap_font.load_font(UI_SETTINGS.DAY_FONT)
    day = label.Label(day_font,text=self.app.data["day"],
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
    for event in self.app.data["events"]:
      entry = displayio.Group()
      bg_color,color = UI_COLOR_MAP[event["color"]]

      # create background for entry
      background = Rectangle(pixel_shader=UI_PALETTE,x=self._margin,y=y,
                             width=self.app.display.width - 2*self._margin,
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

  # --- placeholder image   --------------------------------------------------

  def _get_no_events(self):
    """ return centered image """

    f = open(UI_SETTINGS.NO_EVENTS, "rb")
    pic = displayio.OnDiskBitmap(f)
    x = int((self.app.display.width-pic.width)/2)
    y = int((self.app.display.height-pic.height)/2)
    t = displayio.TileGrid(pic, x=x,y=y, pixel_shader=UI_PALETTE)
    return t

  # --- update data from server   --------------------------------------------

  def update_data(self,app_data):
    """ update data """

    start = time.monotonic()
    try:
      if not self.app.wifi.radio or not self.app.wifi.radio.connected:
        self.app.wifi.connect()
      self.app.data.update(self.app.wifi.get(app_data.data_url).json())
      self.app.wifi.radio.enabled = False
      print(f"update_data (ok): {time.monotonic()-start:f}s")
    except Exception as ex:
      print(f"update_data (exception): {time.monotonic()-start:f}s")
      raise

  # --- create complete content   --------------------------------------------

  def  process_data(self):
    """ create content """

    frame = Frame(self.app.display,self.app.data)

    g = frame.get_group()
    (header,h) = frame.get_header()
    g.append(header)
    gc.collect()

    events = self._get_events()
    if len(events):
      events.y = h + self._margin
      g.append(events)
    else:
      no_events = self._get_no_events()
      g.append(no_events)

    g.append(frame.get_footer())
    self.app.update_display(g)

  # --- handle exception   ---------------------------------------------------

  def handle_exception(self,ex):
    """ handle exception """

    traceback.print_exception(ex)

    g = displayio.Group()
    background = Rectangle(pixel_shader=UI_PALETTE,x=0,y=0,
                           width=self.app.display.width,
                           height=self.app.display.height,
                           color_index=COLORS.WHITE)
    g.append(background)

    f = open(UI_SETTINGS.NO_NETWORK, "rb")
    pic = displayio.OnDiskBitmap(f)
    x = int((self.app.display.width-pic.width)/2)
    y = int((self.app.display.height-pic.height)/2)
    t = displayio.TileGrid(pic, x=x,y=y, pixel_shader=UI_PALETTE)
    g.append(t)

    self.app.update_display(g)
