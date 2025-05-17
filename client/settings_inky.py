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
BTN_PINS  = [board.GPIO5, board.GPIO6, board.GPIO16, board.GPIO24]

class Settings:
  pass

# network configuration   ----------------------------------------------------

secrets = Settings()

secrets.ssid      = 'my-ssid'
secrets.password  = 'my-very-secret-password'
secrets.retry     = 2
secrets.debugflag = False
#secrets.channel   = 6       # optional
#secrets.timeout   = 10      # optional

secrets.time_url = 'http://worldtimeapi.org/api/ip'
secrets.net_update = True    # update time if necessary

# hardware configuration (optional)  -----------------------------------------

hw_config = Settings()

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

def _get_keypad(hal):
  """ return keypad for Inky-Impression """
  import keypad
  return keypad.Keys(BTN_PINS,
                     value_when_pressed=False,pull=True,
                     interval=0.1,max_events=4)

hw_config.DISPLAY = _get_display
hw_config.get_keypad = _get_keypad

# key-mappings (value is index into BTN_PINS)
hw_config.key_on  = 0 # pin A
hw_config.key_upd = 1 # pin B
hw_config.key_off = 2 # pin C

# app configuration   --------------------------------------------------------

app_config = Settings()
app_config.data_url = 'http://my-calendar2json-server-url'
app_config.time_table = [
  ((9,9,1),(0,0,1)),          # from 9 to 9 every hour, i.e. only at 9
  ((9,9,1),(0,0,1)),          # from minute 0 to 0 every minute, i.e. only at 0
  ((9,9,1),(0,0,1)),
  ((9,9,1),(0,0,1)),
  ((9,9,1),(0,0,1)),
  (None,None),
  (None,None)
 ]
