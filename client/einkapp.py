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

from secrets import secrets

# --- application class   ----------------------------------------------------

class EInkApp:

  # --- constructor   --------------------------------------------------------

  def __init__(self,contentprovider,with_rtc=True):
    """ constructor """

    self._setup(with_rtc)  # setup hardware
    self.blink(0.1)
    if with_rtc:
      self._rtc_ext.update()   # update internal rtc from external rtc/internet
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
      self.msg(f"info: no board specific HAL")
      hal_file = "hal.hal_default"
      hal = builtins.__import__(hal_file,None,None,["impl"],0)
      self.msg("info: using default implementation from HalBase")
    return hal

  def _setup(self,with_rtc):
    """ setup hardware """

    hal = self._get_hal()
    
    self.display    = hal.impl.get_display()
    self.is_pygame  = hasattr(self.display,"check_quit")
    self.bat_level  = hal.impl.bat_level
    self.led        = hal.impl.led
    self.keypad     = hal.impl.get_keypad()
    self.wifi       = hal.impl.wifi(self._debug)
    self._shutdown  = hal.impl.shutdown
    self.sleep      = hal.impl.sleep
    self._show      = hal.impl.show
    if with_rtc:
      self._rtc_ext = hal.impl.get_rtc_ext()
      if self._rtc_ext:
        self._rtc_ext.set_wifi(self.wifi)

    gc.collect()

  # --- update data from server   --------------------------------------------

  def update_data(self):
    """ update data """

    start = time.monotonic()
    self.data = {}
    self.data["bat_level"] = self.bat_level()
    self._cprovider.update_data(secrets.app_data)

  # --- update display   -----------------------------------------------------

  def update_display(self,content):
    """ update display """

    # and show content on screen
    start = time.monotonic()
    self._show(content)
    duration = time.monotonic()-start
    self.msg(f"show (HAL): {duration:f}s")

  # --- blink status-led   ---------------------------------------------------

  def blink(self,duration):
    """ blink status-led once for the given duration """
    self.led(1)
    time.sleep(duration)
    self.led(0)

  # --- shutdown device   ----------------------------------------------------

  def shutdown(self):
    """ turn off device after setting next wakeup """
    if self._rtc_ext and getattr(secrets.app_data,"time_table",None):
      wakeup = self._rtc_ext.get_table_alarm(secrets.app_data.time_table)
      self._rtc_ext.set_alarm(wakeup)
    self._shutdown()

  # --- main application loop   ----------------------------------------------

  def run(self):
    """ main application loop """

    # pygame test-environment
    if self.is_pygame:
      try:
        self.update_data()
        self._cprovider.process_data()
      except Exception as ex:
        self._cprovider.handle_exception(ex)
      while True:
        if self.display.check_quit():
          self.shutdown()
        time.sleep(0.5)

    # running on real hardware
    else:
      try:
        self.update_data()
        self._cprovider.process_data()
      except Exception as ex:
        self._cprovider.handle_exception(ex)
      self.shutdown()
      print("update finished, entering endless loop")
      while True:
        time.sleep(60)
