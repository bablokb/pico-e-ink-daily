# ----------------------------------------------------------------------------
# hw_settings_simple.py: Example hw_settings.py with some boilerplate code
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-daily
#
# ----------------------------------------------------------------------------

import board

import busio
from adafruit_bus_device.i2c_device import I2CDevice
import displayio
import fourwire
from adafruit_st7789 import ST7789    # replace this with your driver

# pinout (change to your needs)
SCK_PIN   = board.SCK
MOSI_PIN  = board.MOSI
MISO_PIN  = board.MISO
DC_PIN    = board.GP22
RST_PIN   = board.GP27
CS_PIN    = board.GP12
BUSY_PIN  = board.GP17
BTN_PINS  = [board.GP5, board.GP6, board.GP16]

WIDTH = 320
HEIGHT = 280

class Settings:
  pass

# --- create display   ---------------------------------------------------

def _get_display(config):
  """ create display for Inky-Impression """

  displayio.release_displays()
  spi = busio.SPI(SCK_PIN,MOSI=MOSI_PIN,MISO=MISO_PIN)
  display_bus = fourwire.FourWire(
    spi, command=DC_PIN, chip_select=CS_PIN, reset=RST_PIN, baudrate=1000000
  )

  # replace with your driver
  display = ST7789(display_bus,busy_pin=BUSY_PIN,width=WIDTH,height=HEIGHT)
  display.auto_refresh = False
  return display

def _get_keypad(hal):
  """ return keypad """
  import keypad
  return keypad.Keys(BTN_PINS,
                     value_when_pressed=False,pull=True,
                     interval=0.1,max_events=4)

hw_config = Settings()
hw_config.DISPLAY = _get_display
hw_config.get_keypad = _get_keypad

# key-mappings (value is index into BTN_PINS)
hw_config.key_on  = 0 # pin A
hw_config.key_upd = 1 # pin B
hw_config.key_off = 2 # pin C
