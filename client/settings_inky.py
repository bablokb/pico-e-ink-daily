# ----------------------------------------------------------------------------
# hw_settings_inky.py: Example hw_settings.py for Pimoroni Inky-Impression
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
import struct
import displayio
import fourwire

# pinout for Pimoroni Inky-Impression
SCK_PIN   = board.SCLK
MOSI_PIN  = board.MOSI
MISO_PIN  = board.MISO
DC_PIN    = board.GPIO22
RST_PIN   = board.GPIO27
CS_PIN    = board.CE0
BUSY_PIN  = board.GPIO17

class Settings:
  pass

# --- helper-function for Inky-displays   -------------------------------------

def _get_inky_info():
  """ try to return tuple (width,height,color) """
  COLOR = [None, 'black', 'red', 'yellow', None, 'acep7', 'e673', 'el133']

  EE_ADDR = 0x50
  i2c_device = I2CDevice(board.I2C(),EE_ADDR)
  buffer = bytearray(29)
  with i2c_device as i2c:
    i2c.write(bytes([0x00])+bytes([0x00]))
    i2c.write_then_readinto(bytes([0x00]),buffer)

  data = struct.unpack('<HHBBB22s',buffer)
  if data[4] == 22:
    return [data[0],data[1],'e673']
  elif data[4] == 21:
    return [data[0],data[1],'el133']
  else:
    return [data[0],data[1],COLOR[data[2]]]

def _get_display(config):
  """ create display for Inky-Impression """

  displayio.release_displays()
  width,height,inky_type = _get_inky_info()
  spi = busio.SPI(SCK_PIN,MOSI=MOSI_PIN,MISO=MISO_PIN)
  display_bus = fourwire.FourWire(
    spi, command=DC_PIN, chip_select=CS_PIN, reset=RST_PIN, baudrate=1000000
  )
  if inky_type == 'acep7':
    import adafruit_spd1656
    display = adafruit_spd1656.SPD1656(display_bus,busy_pin=BUSY_PIN,
                                       width=width,height=height,
                                       refresh_time=28,
                                       seconds_per_frame=40)
  elif inky_type == 'e673':
    import spectra6
    display = spectra6.Inky_673(display_bus,busy_pin=BUSY_PIN)
  else:
    raise ValueError("unsupported display")
  display.auto_refresh = False
  return display

hw_setting = Settings()
hw_setting.display = _get_display
