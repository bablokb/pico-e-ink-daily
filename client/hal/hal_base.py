# ----------------------------------------------------------------------------
# HalBase: Hardware-Abstraction-Layer base-class.
#
# This class implements standard methods. If necessary, some of them must be
# overridden by board-specific sub-classes.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/cp-departure-monitor
# ----------------------------------------------------------------------------

import board
import time
try:
  import alarm
except:
  pass
from digitalio import DigitalInOut, Direction

try:
  from settings import hw_config
except:
  pass

class HalBase:
  def __init__(self):
    """ constructor """
    self._display = None
    self._keypad = None
    self.I2C  = self._get_attrib('I2C')
    self.SDA  = self._get_attrib('SDA')
    self.SCL  = self._get_attrib('SCL')
    self.SPI  = self._get_attrib('SPI')
    self.SCK  = self._get_attrib('SCK')
    self.MOSI = self._get_attrib('MOSI')
    self.MISO = self._get_attrib('MISO')

  def _get_attrib(self,attrib):
    """ get attribute from board or from settings """
    value = getattr(board,attrib,None)
    if value is None:
      try:
        value = getattr(hw_config,attrib,None)
      except:
        pass
    return value

  def _init_led(self):
    """ initialize LED/Neopixel """
    if hasattr(board,'NEOPIXEL'):
      if not hasattr(self,'_pixel'):
        if hasattr(board,'NEOPIXEL_POWER'):
          # need to do this first,
          # https://github.com/adafruit/Adafruit_CircuitPython_MagTag/issues/75
          self._pixel_poweroff = DigitalInOut(board.NEOPIXEL_POWER)
          self._pixel_poweroff.direction = Direction.OUTPUT
        import neopixel
        self._pixel = neopixel.NeoPixel(board.NEOPIXEL,1,
                                        brightness=0.1,auto_write=False)
    else:
      led = self._get_attrib('LED')
      if led and not hasattr(self,'_led'):
        self._led = DigitalInOut(led)
        self._led.direction = Direction.OUTPUT

    # replace method with noop
    self._init_led = lambda: None

  def led(self,value,color=[255,0,0]):
    """ set status LED/Neopixel """
    self._init_led()
    if hasattr(self,'_pixel'):
      if hasattr(self,'_pixel_poweroff'):
        self._pixel_poweroff.value = not value
      if value:
        self._pixel.fill(color)
        self._pixel.show()
      elif not hasattr(self,'_pixel_poweroff'):
        self._pixel.fill(0)
        self._pixel.show()
    elif hasattr(self,'_led'):
      self._led.value = value

  def bat_level(self):
    """ return battery level """
    if hasattr(board,"VOLTAGE_MONITOR"):
      from analogio import AnalogIn
      adc = AnalogIn(board.VOLTAGE_MONITOR)
      level = adc.value *  3 * 3.3 / 65535
      adc.deinit()
      return level
    else:
      return 0.0

  def wifi(self,debug=False):
    """ return wifi-interface """
    from wifi_helper_builtin import WifiHelper
    return WifiHelper(debug=debug)

  def get_display(self):
    """ return display """
    if not self._display:
      self._display = self._get_attrib('DISPLAY')
      if callable(self._display):
        # from hw_config!
        self._display = self._display(self)
    return self._display

  def show(self,content):
    """ show and refresh the display """

    self._display.root_group = content

    if hasattr(self._display,"time_to_refresh"):
      if self._display.time_to_refresh > 0.0:
        # ttr will be >0 only if system is on running on USB-power
        time.sleep(2*self._display.time_to_refresh)

    while True:
      try:
        self._display.refresh()
        while self._display.busy:
          time.sleep(0.1)
        break
      except RuntimeError:
        pass

  def get_rtc_ext(self,net_update=False):
    """ return external rtc, if available """
    try:
      return hw_config.get_rtc_ext(net_update=net_update)
    except:
      return None

  def shutdown(self):
    """ shutdown system """
    shutdown = self._get_attrib('shutdown')
    if shutdown:
      shutdown()

  def sleep(self,duration):
    """ sleep for the given duration in seconds """
    time.sleep(duration)

  def get_keypad(self):
    """ return configured keypad """
    try:
      if not self._keypad:
        self._keypad = hw_config.get_keypad(self)
      return self._keypad
    except:
      return None

  def check_key(self,name):
    """ check if key is pressed """

    nr = getattr(hw_config,name,None)
    if nr is None:
      return False
    queue = self.get_keypad.events
    event = queue.get()
    return event and event.pressed and event.key_number == nr

  def deep_sleep(self,alarms=[]):
    """ activate deep-sleep """

    ds = getattr(hw_config,"deep_sleep",None)
    if ds:
      ds(alarms)
    else:
      try:
        alarm.exit_and_deep_sleep_until_alarms(*alarms)
      except:
        while True:
          time.sleep(1)
