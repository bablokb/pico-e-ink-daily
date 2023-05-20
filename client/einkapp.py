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
import alarm
import board
import rtc

# import board-specific implementations
try:
  config_file = "config."+board.board_id.replace(".","_")
  hw_impl = builtins.__import__(config_file,None,None,["config"],0)
  print("using board-specific implementation")
except:
  raise
  config_file = "config.def_config"
  hw_impl = builtins.__import__(config_file,None,None,["config"],0)
  print("using default implementation")

from config.secrets import secrets

# --- application class   ----------------------------------------------------

class EInkApp:

  # --- constructor   --------------------------------------------------------

  def __init__(self,contentprovider,errorhandler,with_rtc=True):
    """ constructor """

    self._setup(with_rtc)  # setup hardware
    if with_rtc:
      self.init_rtc()     # basic settings, clear alarms etc.
      self.update_rtc()   # update internal rtc from external rtc/internet

    self._cprovider = contentprovider
    self._ehandler  = errorhandler
    self._cprovider.set_display(self._display)
    self._ehandler.set_display(self._display)

  # --- setup hardware   -----------------------------------------------------

  def _setup(self,with_rtc):
    """ setup hardware """
    
    self._display   = hw_impl.config.get_display()
    self._bat_level = hw_impl.config.bat_level
    self._led       = hw_impl.config.status_led
    self._wifi      = hw_impl.config.wifi()
    if with_rtc:
      self._rtc_ext   = hw_impl.config.get_rtc_ext()
    self._shutdown  = hw_impl.config.shutdown

  # --- check state of external RTC   ---------------------------------------

  def _check_rtc(self):
    """ check if RTC has a technically valid time """

    ts = self._rtc.datetime
    return (ts.tm_year > 2022 and ts.tm_year < 2099 and
            ts.tm_mon > 0 and ts.tm_mon < 13 and
            ts.tm_mday > 0 and ts.tm_mday < 32 and
            ts.tm_hour < 25 and ts.tm_min < 60 and ts.tm_sec < 60)

  # --- init rtc   -----------------------------------------------------------

  def init_rtc(self):
    """ init rtc """

    # clear any pending alarms
    if hasattr(self._rtc_ext,"alarm1"):
      self._rtc_ext.alarm1_status    = False
      self._rtc_ext.alarm1_interrupt = False
    elif hasattr(self._rtc_ext,"alarm"):
      self._rtc_ext.alarm_status    = False
      self._rtc_ext.alarm_interrupt = False

    # disable clockout
    if hasattr(self._rtc_ext,"clockout_enabled"):
      self._rtc_ext.clockout_enabled = False
    elif hasattr(self._rtc_ext,"clockout_frequency"):
      self._rtc_ext.clockout_frequency = self._rtc_ext.CLOCKOUT_FREQ_DISABLED

  # --- update rtc   ---------------------------------------------------------

  def update_rtc(self):
    """ update rtc """

    # update internal rtc to valid date
    if not self._check_rtc():
      if not self.fetch_time():
        print("setting time to 2022-01-01 12:00:00")
        self._rtc_ext = time.struct_time((2022,1,1,12,00,00,5,1,-1))
    else:
      print("updating internal rtc from external rtc")

    ext_ts = self._rtc_ext.datetime
    rtc.RTC().datetime = ext_ts

  # --- update time from time-server   ---------------------------------------

  def fetch_time():
    """ update time from time-server """

    try:
      self._wifi.connect()
      response = self._wifi.get(secrets.time_url).json()
      print(f"updating time from {secrets.time_url}")
    except Exception as ex:
      return False

    if 'struct_time' in response:
      self._rtc_ext.datetime = time.struct_time(tuple(response['struct_time']))
      return True

    current_time = response["datetime"]
    the_date, the_time = current_time.split("T")
    year, month, mday = [int(x) for x in the_date.split("-")]
    the_time = the_time.split(".")[0]
    hours, minutes, seconds = [int(x) for x in the_time.split(":")]

    year_day = int(response["day_of_year"])
    week_day = int(response["day_of_week"])
    week_day = 6 if week_day == 0 else week_day-1
    is_dst   = int(response["dst"])

    self._rtc_ext = time.struct_time(
      (year, month, mday, hours, minutes, seconds, week_day, year_day, is_dst))
    return True

  # --- set alarm-time   ----------------------------------------------------

  def set_alarm(self,d=None,h=None,m=None,s=None,alarm_time=None):
    """ set alarm-time. DS3231 has alarm1, while PCF85x3 has alarm """

    # you can pass either a fixed date (alarm_time) or an interval
    # in days, hours, minutes, seconds
    if alarm_time is None:
      sleep_time = 0
      if d is not None:
        sleep_time += d*86400
      if h is not None:
        sleep_time += h*3600
      if m is not None:
        sleep_time += m*60
      if s is not None:
        sleep_time += s
      if sleep_time == 0:
        return
      now = time.localtime()
      alarm_time = time.localtime(time.mktime(now) + sleep_time)

    print("Next rtc-wakup: %04d-%02d-%02d %02d:%02d:%02d" %
          (alarm_time.tm_year,alarm_time.tm_mon,alarm_time.tm_mday,
           alarm_time.tm_hour,alarm_time.tm_min,alarm_time.tm_sec)
          )

    if hasattr(self._rtc_ext,"alarm1"):
      self._rtc_ext.alarm1  = (alarm_time,"daily")
      self._rtc_ext.alarm1_interrupt = True
    elif hasattr(self._rtc_ext,"alarm"):
      self._rtc_ext.alarm  = (alarm_time,"daily")
      self._rtc_ext.alarm_interrupt = True

  # --- update data from server   --------------------------------------------

  def update_data(self):
    """ update data """

    start = time.monotonic()
    self._data = {}
    self._data["bat_level"] = self._bat_level()
    try:
      if not self._wifi.connected:
        self._wifi.connect()
      self._data.update(self._wifi.get(secrets.data_url))
      self._wifi.enabled = False
      print(f"update_data (ok): {time.monotonic()-start:f}s")
    except Exception as ex:
      self._ehandler.on_exception(ex)
      print(f"update_data (exception): {time.monotonic()-start:f}s")
      raise

  # --- update display   -----------------------------------------------------

  def update_display(self,content):
    """ update display """

    start = time.monotonic()
    self._display.show(content)
    print(f"update_display (show): {time.monotonic()-start:f}s")
    start = time.monotonic()
    if self._display.time_to_refresh > 0.0:
      # ttr will be >0 only if system is on USB-power (running...)
      print(f"time-to-refresh: {self._display.time_to_refresh}")
      time_alarm = alarm.time.TimeAlarm(
        monotonic_time=time.monotonic()+self._display.time_to_refresh)
      alarm.light_sleep_until_alarms(time_alarm)
    self._display.refresh()
    duration = time.monotonic()-start
    print(f"update_display (refreshed): {duration:f}s")
    update_time = self._display.time_to_refresh - duration
    if update_time > 0.0:
      print(f"update-time: {update_time}")
      time_alarm = alarm.time.TimeAlarm(
        monotonic_time=time.monotonic()+update_time)
      alarm.light_sleep_until_alarms(time_alarm)

  # --- blink status-led   ---------------------------------------------------

  def blink(self,duration):
    """ blink status-led once for the given duration """
    self._led(1)
    time.sleep(duration)
    self._led(0)

  # --- shutdown device   ----------------------------------------------------

  def shutdown(self):
    """ turn off device """
    self._shutdown()

  # --- main application loop   ----------------------------------------------

  def run(self):
    """ main application loop """

    # pygame test-environment
    if hasattr(self._display,"check_quit"):
      try:
        self.update_data()
        self.update_display(self._cprovider.get_content(self._data))
      except:
        self.update_display(self._ehandler.get_content())
      while True:
        if self._display.check_quit():
          self.shutdown()
        time.sleep(0.5)

    # running on real hardware
    else:
      try:
        self.update_data()
        self.update_display(self._cprovider.get_content(self._data))
      except:
        self.update_display(self._ehandler.get_content())
      self.shutdown()
      time.sleep(60)
