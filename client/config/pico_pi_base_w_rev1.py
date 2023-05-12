# ----------------------------------------------------------------------------
# pico_pi_base.py: HW-config for Pico Pi Base, pcb-en-control and Inky-Impression
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
import displayio
import adafruit_spd1656
from digitalio import DigitalInOut, Direction, Pull

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

  def get_display(self):
    """ return display """
    displayio.release_displays()
    spi = busio.SPI(SCK_PIN,MOSI=MOSI_PIN,MISO=MISO_PIN)
    display_bus = displayio.FourWire(
      spi, command=DC_PIN, chip_select=CS_PIN_D, reset=RST_PIN, baudrate=1000000
    )
    display = adafruit_spd1656.SPD1656(display_bus,busy_pin=BUSY_PIN,
                                       width=600,height=448,
                                       refresh_time=2,
                                       seconds_per_frame=40)
    display.auto_refresh = False
    return display

  def get_rtc_ext(self):
    """ return external rtc, if available """
    try:
      from adafruit_pcf8563 import PCF8563
      i2c = board.I2C()
      return PCF8563(i2c)
    except:
      return None

  def shutdown(self):
    """ turn off power by pulling GP4 high """
    self._done.value = 1
    time.sleep(0.2)
    self._done.value = 0
    time.sleep(0.5)

config = PicoPiBaseConfig()
