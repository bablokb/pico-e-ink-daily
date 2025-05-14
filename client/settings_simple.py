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

hw_setting = Settings()
hw_setting.display = _get_display
