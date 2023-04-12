#!/usr/bin/python3
# ----------------------------------------------------------------------------
# A simplistic HTTP-server that returns calendar-entries as a json-structure.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/py-calendar2json
#
# ----------------------------------------------------------------------------

CONFIG_FILE = "py-calendar2json.json"

import caldav
import pytz
import datetime
from operator import itemgetter
import locale, http.server, json, signal, os, sys
from   argparse import ArgumentParser

# --- helper class to convert a dict to an object   --------------------------

class Options:
  def add(self,d):
    for key in d:
      setattr(self,key,d[key])

# --- handler class   --------------------------------------------------------

class Calendar2json(http.server.BaseHTTPRequestHandler):
  """ Request-handler class """

  def log_request(*args,**kw):
    """ prevent logging unless in debug mode """
    if settings.debug:
      http.server.BaseHTTPRequestHandler.log_request(*args,**kw)

  def do_GET(self):
    """ process get-requests """

    data = self._get_agenda()
    json_data = json.dumps(data,indent=2).encode(encoding='utf_8')
    self.send_response(http.HTTPStatus.OK.value)
    self.send_header("Content-Type","application/json")
    self.send_header("Content-Length",str(len(json_data)))
    self.end_headers()
    self.wfile.write(json_data)

  # --- read agendas from caldav-servers   ------------------------------------

  def _get_agenda(self):
    """ read agenda for all configured calendars """

    entries = []
    for cal_info in settings.cals:
      self._get_agenda_for_cal(cal_info,entries)
    entries.sort(key=itemgetter('start'))
    return entries

  # --- read agenda from caldav-server   --------------------------------------

  def _get_agenda_for_cal(self,cal_info,entries):
    """ read agenda from caldav-server """

    start_of_day = datetime.datetime.combine(datetime.date.today(),
                                         datetime.time.min)
    end_of_day   = datetime.datetime.combine(datetime.date.today(),
                                         datetime.time.max)

    tz_local  = pytz.timezone(settings.TZ_NAME)
    now = datetime.datetime.now(tz_local)

    client = caldav.DAVClient(url=cal_info["dav_url"],
                                username=cal_info["dav_user"],
                                password=cal_info["dav_pw"])

    # get calendar by name
    calendars = client.principal().calendars()
    cal = next(c for c in calendars if c.name == cal_info["cal_name"])

    # extract relevant data
    cal_events = cal.date_search(start=start_of_day,end=end_of_day,expand=True)
    agenda_list = []
    for cal_event in cal_events:
      item = {}
      if hasattr(cal_event.instance, 'vtimezone'):
        tzinfo = cal_event.instance.vtimezone.gettzinfo()
      else:
        tzinfo = tz_local
      components = cal_event.instance.components()
      for component in components:
        if component.name != 'VEVENT':
          continue
        item['dtstart'] = self._get_timeattr(
          component,'dtstart',start_of_day,tzinfo)
        if hasattr(component,'duration'):
          duration = getattr(component,'duration').value
          item['dtend'] = item['dtstart'] + duration
        else:
          item['dtend']   = self._get_timeattr(
            component,'dtend',end_of_day,tzinfo)
        if item['dtend'] < now:
          # ignore old events
          continue
        if item['dtend'].day != item['dtstart'].day:
          item['dtend'] = end_of_day.replace(tzinfo=tz_local)

        for attr in ('summary', 'location'):
          if hasattr(component,attr):
            item[attr] = getattr(component,attr).value
          else:
            item[attr] = ""
        agenda_list.append(item)

    for item in agenda_list:
      entries.append(
        {"start": item['dtstart'].astimezone().strftime("%H:%M"),
         "end":   item['dtend'].astimezone().strftime("%H:%M"),
         "summary": item['summary'],
         "location": item['location'],
         "color": cal_info["cal_color"]
         })

  # --- extract time attribute   ----------------------------------------------

  def _get_timeattr(self,component,timeattr,default,tzinfo):
    """ extract time attribute """

    if hasattr(component,timeattr):
      dt = getattr(component,timeattr).value
      if not isinstance(dt,datetime.datetime):
        dt = datetime.datetime(dt.year, dt.month, dt.day)
    else:
      dt = default
    if not dt.tzinfo:
      dt = tzinfo.localize(dt)
    return dt

# --- signal handler   -------------------------------------------------------

def signal_handler(_signo,_stack_frame):
  """ signal-handler for clean shutdown """
  sys.exit(0)

# --- cmdline-parser   ------------------------------------------------------

def get_parser():
  """ configure cmdline-parser """

  parser = ArgumentParser(add_help=False,description='Calendar2json Server')

  parser.add_argument('-c', '--config', nargs=1,
    metavar='config file', default=None,
    dest='config_file',
    help='configuration file (overwrites /etc/py-calendar2json.json)')

  parser.add_argument('-d', '--debug', action='store_true',
    dest='debug', default=False,
    help="force debug-mode")
  parser.add_argument('-q', '--quiet', action='store_true',
    dest='quiet', default=False,
    help="don't print messages")
  parser.add_argument('-h', '--help', action='help',
    help='print this help')
  return parser

# --- main program   ---------------------------------------------------------

if __name__ == '__main__':

  opt_parser = get_parser()
  settings = Options()
  opt_parser.parse_args(namespace=settings)

  if not settings.config_file:
    settings.config_file = os.path.join("/etc",CONFIG_FILE)
  else:
    settings.config_file = settings.config_file[0]

  with open(settings.config_file,"r") as f:
    settings.add(json.load(f))

  # set local to default from environment
  locale.setlocale(locale.LC_ALL, '')

  # setup signal-handler
  signal.signal(signal.SIGTERM, signal_handler)
  signal.signal(signal.SIGINT,  signal_handler)

  httpd = http.server.HTTPServer(('',settings.PORT),Calendar2json)
  if not settings.quiet:
    print("running Calendar2json-Server on: 0.0.0.0:%d" % settings.PORT)
  httpd.serve_forever()
