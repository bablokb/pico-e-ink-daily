# -------------------------------------------------------------------------
# Generic class for e-ink based applications.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pico-e-ink-daily
#
# -------------------------------------------------------------------------

# --- imports   -----------------------------------------------------------

import builtins
import time
import board
import gc

from settings import secrets, hw_config, app_config

# --- application class   ----------------------------------------------------

class EInkApp:

  # --- constructor   --------------------------------------------------------

  def __init__(self,contentprovider,with_rtc=True):
    """ constructor """

    self._debug = getattr(app_config, "debug", False)
    self._setup(with_rtc)  # setup hardware
    self.blink(0.1)

    # check for power_off pin (unconditional, no automatic wake-up)
    self._check_power_off()

    # update internal rtc from external rtc/internet
    if self._rtc_ext:
      self._rtc_ext.update(force=self._impl.check_key("key_upd"))
    self._cprovider = contentprovider
    self._cprovider.app = self

  # --- get HAL   ------------------------------------------------------------

  # Import HAL (hardware-abstraction-layer).
  # This expects an object "impl" within the implementing hal_file.
  # All hal implementations are within src/hal/. Filenames must be
  # board.board_id.py, e.g. src/hal/pimoroni_inky_frame_5_7.py

  def _get_hal(self):
    """ read and return hal-object """

    try:
      hal_file = "hal."+board.board_id.replace(".","_")
      hal = builtins.__import__(hal_file,None,None,["impl"],0)
      self.msg("using board-specific implementation")
    except Exception as ex:
      self.msg(f"info: no board specific HAL (ex: {ex})")
      hal_file = "hal.hal_default"
      hal = builtins.__import__(hal_file,None,None,["impl"],0)
      self.msg("info: using default implementation from HalBase")
    return hal

  def _setup(self,with_rtc):
    """ setup hardware """

    self._impl = self._get_hal().impl
    self._impl.debug = self._debug
    
    self.display    = self._impl.get_display()
    self.is_pygame  = hasattr(self.display,"check_quit")
    self.wifi       = self._impl.wifi(self._debug)

    if with_rtc:
      self._rtc_ext = self._impl.get_rtc_ext()

    gc.collect()

  # --- check for power-off button press   -----------------------------------

  def _check_power_off(self):
    """ check power_off button """

    if  self._impl.check_key("key_off"):
      blink_time = getattr(hw_config,"led_blinktime",0.1)
      for _ in range(3):
        self.blink(blink_time)
      time.sleep(1)                   # extra time for button release
      self._impl.shutdown()           # direct shutdown, no wake-up
      self._impl.deep_sleep()         # in case shutdown is noop

  # --- print debug-message   ------------------------------------------------

  def msg(self,text):
    """ print (debug) message """
    if self._debug:
      print(text)

  # --- update data from server   --------------------------------------------

  def update_data(self):
    """ update data """

    start = time.monotonic()
    self.data = {}
    self.data["bat_level"] = self._impl.bat_level()
    self._cprovider.update_data(app_config)

  # --- update display   -----------------------------------------------------

  def update_display(self,content):
    """ update display """

    start = time.monotonic()

    self.display.root_group = content

    if hasattr(self.display,"time_to_refresh"):
      if self.display.time_to_refresh > 0.0:
        # ttr will be >0 only if system is on running on USB-power
        time.sleep(self.display.time_to_refresh)

    try:
      self.display.refresh()
      if hasattr(self.display,"busy"):
        while self.display.busy:
          time.sleep(0.1)
    except RuntimeError:
      pass

    duration = time.monotonic()-start
    self.msg(f"update display: {duration:f}s")

  # --- blink status-led   ---------------------------------------------------

  def blink(self,duration):
    """ blink status-led once for the given duration """
    self._impl.led(1)
    time.sleep(duration)
    self._impl.led(0)

  # --- shutdown device   ----------------------------------------------------

  def shutdown(self):
    """ turn off device after setting next wakeup """
    if self._rtc_ext and getattr(app_config,"time_table",None):
      wakeup = self._rtc_ext.get_table_alarm(app_config.time_table)
      self._rtc_ext.set_alarm(wakeup)
    self._impl.shutdown()

  # --- cleanup ressources at exit   -----------------------------------------

  def at_exit(self):
    """ cleanup ressources """
    self._impl.at_exit()

  # --- run single execution   -----------------------------------------------

  def run_once(self):
    """ single execution main processing """

    try:
      self.update_data()
      content = self._cprovider.create_view()
      self.update_display(content)
    except Exception as ex:
      self._cprovider.handle_exception(ex)
    self.shutdown()                        # pygame will instead wait for quit
    self._impl.deep_sleep()                # in case shutdown is a noop
