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

class UIApplication:

  RED   = [255,0,0]
  GREEN = [0,255,0]

  # --- constructor   --------------------------------------------------------

  def __init__(self,dataprovider,uiprovider,with_rtc=True):
    """ constructor """

    self._debug = getattr(app_config, "debug", False)
    self._setup(with_rtc)  # setup hardware
    blink_time = getattr(hw_config,"led_blink_init",0.1)
    self.blink(blink_time)

    # check for power_off pin (unconditional, no automatic wake-up)
    self._check_power_off()

    # update internal rtc from external rtc/internet
    if self._rtc_ext:
      self._rtc_ext.update(force=self._impl.check_key("key_upd"))
    self._dataprovider = dataprovider
    self._dataprovider.set_wifi(self._impl.wifi(debug=secrets.debugflag))
    self._uiprovider = uiprovider
    self.data = {}

  # --- get HAL   ------------------------------------------------------------

  # Import HAL (hardware-abstraction-layer).
  # This expects an object "impl" within the implementing hal_file.
  # All hal implementations are within src/hal/. Filenames must be
  # board.board_id.py, e.g. src/hal/pimoroni_inky_frame_5_7.py

  def _get_hal(self):
    """ read and return hal-object """

    try:
      hal_file = "base_app.hal."+board.board_id.replace(".","_")
      hal = builtins.__import__(hal_file,None,None,["impl"],0)
      self.msg("using board-specific implementation")
    except Exception as ex:
      self.msg(f"info: no board specific HAL (ex: {ex})")
      hal_file = "base_app.hal.hal_default"
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
      self._rtc_ext = self._impl.get_rtc_ext(net_update=True,debug=self._debug)

    gc.collect()

  # --- check for power-off button press   -----------------------------------

  def _check_power_off(self):
    """ check power_off button """

    if  self._impl.check_key("key_off"):
      blink_time = getattr(hw_config,"led_blink_power_off",0.1)
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

  # --- blink status-led   ---------------------------------------------------

  def blink(self,duration,color=RED):
    """ blink status-led once for the given duration """
    self._impl.led(1,color=color)
    time.sleep(duration)
    self._impl.led(0,color=color)

  # --- update data from server   --------------------------------------------

  def update_data(self):
    """ update data """

    blink_time = getattr(hw_config,"led_blink_data",0.3)
    self.blink(blink_time,color=UIApplication.RED)
    self.data["bat_level"] = self._impl.bat_level()

    start = time.monotonic()
    self._dataprovider.update_data(self.data)
    duration = time.monotonic()-start
    self.blink(blink_time,color=UIApplication.GREEN)
    self.msg(f"update_data (dataprovider): {duration:f}s")

  # --- handle data-exception   ----------------------------------------------

  def handle_exception(self,ex):
    """ pass exception of data-provider to ui-provider """

    blink_time = getattr(hw_config,"led_blink_exception",0.6)
    self.blink(blink_time,color=UIApplication.RED)
    start = time.monotonic()
    self.update_display(self._uiprovider.handle_exception(ex))
    duration = time.monotonic()-start
    self.msg(f"handle_exception (uiprovider): {duration:f}s")

  # --- create ui   ----------------------------------------------------------

  def create_ui(self):
    """ create UI. UI-provider might buffer UI for performance """

    start = time.monotonic()
    self._uiprovider.create_ui(self.display)
    duration = time.monotonic()-start
    self.msg(f"create_ui (uiprovider): {duration:f}s")

  # --- free memory from UI   ------------------------------------------------

  def free_ui_memory(self):
    """ free memory used by UI and display """

    if not self.is_pygame:
      self.msg(f"free memory before clear of UI: {gc.mem_free()}")
      self.display.root_group = None
      self._uiprovider.clear_ui()
      #gc.collect()
      self.msg(f"free memory after clear of UI: {gc.mem_free()}")

  # --- update display   -----------------------------------------------------

  def update_display(self,content=None):
    """ update display """

    # update UI with current model
    if not content:
      start = time.monotonic()
      self._ui = self._uiprovider.update_ui()
      duration = time.monotonic()-start
      self.msg(f"update_ui (uiprovider): {duration:f}s")

    # and show content on screen
    start = time.monotonic()
    if content:
      self.display.root_group = content
    else:
      self.display.root_group = self._ui
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

  # --- shutdown device   ----------------------------------------------------

  def shutdown(self,rc):
    """ turn off device after setting next wakeup """
    self.msg(f"shutdown with {rc=}:")
    if rc:
      if self._rtc_ext and getattr(app_config,"time_table",None):
        wakeup = self._rtc_ext.get_table_alarm(app_config.time_table)
        self._rtc_ext.set_alarm(wakeup)
      else:
        self.msg("could not configure wakeup")
    else:
      self.msg("not configuring wakeup due to exception")
    self._impl.shutdown()

  # --- cleanup ressources at exit   -----------------------------------------

  def at_exit(self):
    """ cleanup ressources """
    self._impl.at_exit()

  # --- run single execution   -----------------------------------------------

  def run_once(self):
    """ single execution main processing """

    try:
      self.create_ui()      # ui-provider should buffer this for performance
      self.update_data()
      self.update_display()
      rc = True
    except Exception as ex1:
      self.msg(f"failed: {ex1=}")
      try:
        self.handle_exception(ex1)
      except Exception as ex2:
        self.msg(f"failed to handle exception: {ex2=}")
      rc = False

    self.shutdown(rc)                      # pygame will instead wait for quit
    self._impl.deep_sleep()                # in case shutdown is a noop
