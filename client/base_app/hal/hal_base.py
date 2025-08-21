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
    self.debug = False
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
    """ get attribute from hw_config, hal or board """
    for obj in [hw_config, self, board]:
      value = getattr(obj,attrib,None)
      if not value is None:
        return value
    return value

  def _init_led(self):
    """ initialize LED/Neopixel """
    if hasattr(self,'_led') or hasattr(self,'_pixel'):
      return
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

  def msg(self,*args):
    """ print debug-message """
    if self.debug:
      print(*args)

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
    from ..wifi_impl_builtin import WifiImpl
    return WifiImpl(debug=debug)

  def get_display(self):
    """ return display """
    if not self._display:
      self._display = self._get_attrib('DISPLAY')
      if callable(self._display):
        # from hw_config!
        self._display = self._display(self)
    return self._display

  def get_rtc_ext(self,net_update=False,debug=False):
    """ return external rtc, if available """
    try:
      return hw_config.get_rtc_ext(net_update=net_update,debug=debug)
    except:
      return None

  def shutdown(self):
    """ shutdown system """
    shutdown = self._get_attrib('shutdown')
    if shutdown and shutdown != self.shutdown:
      shutdown()

  def at_exit(self):
    """ exit processing """
    self.msg("hal_base.at_exit()")
    try:
      if not hasattr(board,"DISPLAY"):
        import displayio
        displayio.release_displays()
    except:
      pass
    try:
      self._keypad.deinit()
    except:
      pass

  def sleep(self,duration):
    """ sleep for the given duration in seconds """
    time.sleep(duration)

  def get_keypad(self):
    """ return configured keypad """
    try:
      if not self._keypad:
        self._keypad = hw_config.get_keypad(self)
        self._keypad.reset()
        time.sleep(0.1)   # wait for keypad-scan (default scan-interval is 0.02)
      return self._keypad
    except:
      return None

  def check_key(self,name):
    """ check if key is pressed """

    nr = getattr(hw_config,name,None)
    self.msg(f"check_key({name}): {nr=}")
    if nr is None:
      return False
    keypad = self.get_keypad()
    if not keypad:
      return False
    queue = keypad.events
    ev = queue.get()
    if ev:
      self.msg(f"check_key({name}): pressed: {ev.pressed}, knr: {ev.key_number}")
      return ev.pressed and ev.key_number == nr
    else:
      self.msg("ckeck_key({name}): empty event-queue")

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
