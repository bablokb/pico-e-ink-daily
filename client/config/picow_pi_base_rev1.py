# ----------------------------------------------------------------------------
# picow_pi_base_rev1.py: config for Pico Pi Base, pcb-en-control and Inky-Impression
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-daily
#
# ----------------------------------------------------------------------------

import board

from hwconfig import HWConfig
import busio
from adafruit_bus_device.i2c_device import I2CDevice
import struct
import displayio
import adafruit_spd1656
from digitalio import DigitalInOut, Direction

# pinout for Pimoroni Inky-Impression
SCK_PIN   = board.SCLK
MOSI_PIN  = board.MOSI
MISO_PIN  = board.MISO
DC_PIN    = board.GPIO22
RST_PIN   = board.GPIO27
CS_PIN_D  = board.CE0
BUSY_PIN  = board.GPIO17

DONE_PIN  = board.GP4

class PicoPiBaseConfig(HWConfig):
  """ pico-pi-base specific configuration-class """

  def __init__(self):
    """ constructor """
    self._done           = DigitalInOut(DONE_PIN)
    self._done.direction = Direction.OUTPUT
    self._done.value     = 0

  def _get_size(self):
    """ try to read the eeprom """
    i2c_device = I2CDevice(board.I2C(),EE_ADDR)
    with i2c_device as i2c:
      i2c.write(bytes([register])+bytes(data))


  def get_display(self):
    """ return display """
    displayio.release_displays()
    width,height = self._get_size()
    spi = busio.SPI(SCK_PIN,MOSI=MOSI_PIN,MISO=MISO_PIN)
    display_bus = displayio.FourWire(
      spi, command=DC_PIN, chip_select=CS_PIN_D, reset=RST_PIN, baudrate=1000000
    )
    display = adafruit_spd1656.SPD1656(display_bus,busy_pin=BUSY_PIN,
                                       width=width,height=height,
                                       refresh_time=2,
                                       seconds_per_frame=40)
    display.auto_refresh = False
    return display

  def get_rtc_ext(self):
    """ return external rtc, if available """
    try:
      from rtc_ext.pcf8563 import ExtPCF8563
      i2c = board.I2C()
      return ExtPCF8563(i2c)
    except:
      return None

  def shutdown(self):
    """ turn off power by pulling GP4 high """
    self._done.value = 1
    time.sleep(0.2)
    self._done.value = 0
    time.sleep(0.5)

config = PicoPiBaseConfig()
